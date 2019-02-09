import os
import json
from datetime import datetime
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

        now = datetime.utcnow().isoformat() + 'Z'
        competitions_info = []
        for info in api.competitions_list():
            deadline = getattr(info, 'deadline')
            deadline = datetime.strftime(deadline, '%Y-%m-%d %H:%M:%S')
            if now <= deadline:
                competitions_info.append(info)
        return competitions_info
    except Exception as e:
        LOGGER.error(e)


def create_events(competitions_list):
    for competition_info in competitions_list:
        created_flg = False
        calendar_id_list = get_calendar_id_list(competition_info)

        for calendar_id in calendar_id_list:
            try:
                competition_name = getattr(competition_info, 'title')
                if not event_exists(calendar_id, competition_name):
                    body = get_calendar_body(competition_info)
                    event = SERVICE.events().insert(calendarId=calendar_id, body=body).execute()
                    created_flg = True

                    msg = 'Create event. calendar id: {}, competitions name: {}'.format(
                        calendar_id, competition_name)
                    LOGGER.debug(msg)
            except Exception as e:
                LOGGER.error(e)

        if created_flg:
            post_slack(competition_info)


def get_event_name_list(calendar_id=CALENDAR_JSON['all']['calendar_id']):
    now = datetime.utcnow().isoformat() + 'Z'
    try:
        result = SERVICE.events().list(
            calendarId=calendar_id, timeMin=now).execute()
        event_list = result.get('items', [])

        events_name = []
        for event in events:
            events_name.append(event['summary'])
        return events_name
    except Exception as e:
        LOGGER.error(e)


def event_exists(calendar_id, q):
    try:
        result = SERVICE.events().list(calendarId=calendar_id, q=q,
                                       timeMin=datetime.utcnow().isoformat()+'Z').execute()
        if not result['items']:
            return False
        else:
            return True
    except Exception as e:
        LOGGER.error(e)


def get_calendar_id_list(info):
    id_list = [CALENDAR_JSON['all']['calendar_id']]
    awards_points = getattr(info, 'awardsPoints')
    category = getattr(info, 'category')
    reward = getattr(info, 'reward')

    if awards_points:
        id_list.append(CALENDAR_JSON['awards_points']['calendar_id'])
    if reward.find('$') != -1:
        id_list.append(CALENDAR_JSON['reward']['calendar_id'])

    if category == CALENDAR_JSON['featured']['category']:
        id_list.append(CALENDAR_JSON['featured']['calendar_id'])

    elif category == CALENDAR_JSON['research']['category']:
        id_list.append(CALENDAR_JSON['research']['calendar_id'])

    elif category == CALENDAR_JSON['getting_started']['category']:
        id_list.append(CALENDAR_JSON['getting_started']['calendar_id'])

    elif category == CALENDAR_JSON['playground']['category']:
        id_list.append(CALENDAR_JSON['playground']['calendar_id'])

    else:
        try:
            msg = 'Value is invalid. category: {}'.format(category)
            raise ValueError(msg)
        except ValueError as e:
            LOGGER.error(e)

    return id_list


def get_calendar_body(info):
    summary = getattr(info, 'title')

    # key_list = ['description', 'evaluationMetric', 'isKernelsSubmissionsOnly', 'tags', 'url']
    # description = ''
    # for key in dir(info):
    #     if key in key_list:
    #         description += '{}: {}\n'.format(key,
    #                                             getattr(info, key))
    description = getattr(info, 'url')
    description = description.replace(':80', '')

    start_date = getattr(info, 'enabledDate')
    start_date = timezone('UTC').localize(start_date)
    start_date = start_date.isoformat()

    end_date = getattr(info, 'deadline')
    end_date = timezone('UTC').localize(end_date)
    end_date = end_date.isoformat()

    body = open_json('format/calendar_insert.json')

    body['summary'] = summary
    body['description'] = description
    body['start']['dateTime'] = start_date
    body['end']['dateTime'] = end_date

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
