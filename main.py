import os
import json
import datetime
from pytz import timezone
from logging import StreamHandler, DEBUG, Formatter, FileHandler, getLogger
import requests
from kaggle.api.kaggle_api_extended import KaggleApi
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file


LOGGER = getLogger(__name__)

LOCAL = False

if LOCAL:
    import config
    STORE = file.Storage('credentials/token.json')
    CREDS = STORE.get()
    SERVICE = build('calendar', 'v3', http=CREDS.authorize(Http()))
else:
    CONTENTS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    CREDS = client.Credentials.new_from_json(CONTENTS)
    SERVICE = build('calendar', 'v3', http=CREDS.authorize(Http()))

SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')


def open_json(path):
    try:
        with open(path) as f:
            f_json = f.read()
            f_json = json.loads(f_json)

        msg = 'Load {}'.format(path)
        LOGGER.debug(msg)

        return f_json
    except Exception as e:
        LOGGER.error(e)


CALENDAR_JSON = open_json('calendar.json')


def get_competitions_list():
    try:
        api = KaggleApi()
        api.authenticate()

        now = datetime.datetime.utcnow().isoformat() + 'Z'

        competitions_info = []
        for info in api.competitions_list():
            deadline = getattr(info, 'deadline')
            deadline = datetime.datetime.strftime(
                deadline, '%Y-%m-%d %H:%M:%S')
            if now <= deadline:
                competitions_info.append(info)
        return competitions_info
    except Exception as e:
        LOGGER.error(e)


def create_events(competitions_list):
    for competition_info in competitions_list:
        created_flg = False
        calendar_list = get_calendar_list(competition_info)

        for calendar_name in calendar_list:
            competition_name = getattr(competition_info, 'title')
            calendar_id = CALENDAR_JSON[calendar_name]['id']
            if not event_exists(calendar_id, competition_name):
                body = get_calendar_body(competition_info, calendar_name)
                try:
                    event = SERVICE.events().insert(calendarId=calendar_id, body=body).execute()
                    created_flg = True

                    msg = 'Create event. calendar id: {}, competitions name: {}'.format(
                        calendar_id, competition_name)
                    LOGGER.debug(msg)
                except Exception as e:
                    LOGGER.error(e)

        if created_flg:
            post_slack(competition_info)


def get_event_name_list(calendar_id=CALENDAR_JSON['all']['id']):
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    try:
        result = SERVICE.events().list(
            calendarId=calendar_id, timeMin=now).execute()
    except Exception as e:
        LOGGER.error(e)

    events = result.get('items', [])
    events_name = []
    for event in events:
        events_name.append(event['summary'])
    return events_name


def event_exists(calendar_id, q):
    now = datetime.datetime.utcnow()
    # avoid make 2 events in 2 stage competition
    last_week = now - datetime.timedelta(days=7)
    last_week = last_week.isoformat() + 'Z'

    try:
        result = SERVICE.events().list(calendarId=calendar_id,
                                       q=q, timeMin=last_week).execute()
    except Exception as e:
        LOGGER.error(e)

    if not result['items']:
        return False
    return True


def get_calendar_list(info):
    calendar_list = [CALENDAR_JSON['all']['name']]

    awards_points = getattr(info, 'awardsPoints')
    if awards_points:
        calendar_list.append(CALENDAR_JSON['awards_points']['name'])

    # Class Tag convert to str
    tags = [str(tag) for tag in getattr(info, 'tags')]

    for calendar in CALENDAR_JSON:
        if awards_points and CALENDAR_JSON[calendar]['data'] in tags:
            calendar_list.append(CALENDAR_JSON[calendar]['name'])

    return calendar_list


def get_calendar_body(competition_info, calendar_name):
    summary = getattr(competition_info, 'title')

    # key_list = ['description', 'evaluationMetric', 'isKernelsSubmissionsOnly', 'tags', 'url']
    # description = ''
    # for key in dir(info):
    #     if key in key_list:
    #         description += '{}: {}\n'.format(key,
    #                                             getattr(info, key))
    description = getattr(competition_info, 'url')
    description = description.replace(':80', '')

    start_date = getattr(competition_info, 'enabledDate')
    start_date = timezone('UTC').localize(start_date)
    start_date = start_date.isoformat()

    end_date = getattr(competition_info, 'deadline')
    end_date = timezone('UTC').localize(end_date)
    end_date = end_date.isoformat()

    # Different colors depending on whether there is awards points
    if getattr(competition_info, 'awardsPoints'):
        color_id = CALENDAR_JSON[calendar_name]['colorId_1']
    else:
        color_id = CALENDAR_JSON[calendar_name]['colorId_2']

    body = open_json('format/calendar_insert.json')

    body['summary'] = summary
    body['description'] = description
    body['start']['dateTime'] = start_date
    body['end']['dateTime'] = end_date
    body['colorId'] = color_id

    return body


def post_slack(info):
    title = getattr(info, 'title')
    value = getattr(info, 'url')

    body = open_json('format/slack_post.json')
    body['attachments'][0]['fields'][0]['title'] = title
    body['attachments'][0]['fields'][0]['value'] = value

    try:
        r = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(body))
        msg = 'Post Slack. title: {}, value: {}'.format(title, value)
        LOGGER.debug(msg)
    except Exception as e:
        LOGGER.error(e)


def deleteAllEvent(calendar_id):
    result = SERVICE.events().list(calendarId=calendar_id).execute()
    for event in result['items']:
        result = SERVICE.events().delete(
            calendarId=calendar_id, eventId=event['id']).execute()
        print('delete: {}'.format(event['id']))


def main():
    log_fmt = Formatter(
        '%(asctime)s %(name)s %(lineno)d [%(levelname)s][%(funcName)s] %(message)s ')
    handler = StreamHandler()
    handler.setLevel('INFO')
    handler.setFormatter(log_fmt)
    LOGGER.addHandler(handler)

    handler = StreamHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(log_fmt)
    LOGGER.addHandler(handler)

    competitions_list = get_competitions_list()
    create_events(competitions_list)


main()
# for i in CALENDAR_JSON:
#     deleteAllEvent(CALENDAR_JSON[i]['id'])
