import os
import json
import datetime
from logging import StreamHandler, INFO, DEBUG, Formatter, FileHandler, getLogger

# import dotenv
from kaggle import KaggleApi
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file


logger = getLogger(__name__)
log_fmt = Formatter(
    '%(asctime)s %(name)s %(lineno)d [%(levelname)s][%(funcName)s] %(message)s')
# info
handler = StreamHandler()
handler.setLevel(INFO)
handler.setFormatter(log_fmt)
logger.addHandler(handler)
logger.setLevel(INFO)
# debug
handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(log_fmt)
logger.addHandler(handler)
logger.setLevel(DEBUG)


def new_calendar_service():
    contents = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    creds = client.Credentials.new_from_json(contents)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service


def open_json(path):
    try:
        with open(path) as f:
            f_json = f.read()
            f_json = json.loads(f_json)

        msg = 'Load {}'.format(path)
        logger.debug(msg)
        return f_json
    except Exception as e:
        logger.error(e)


def get_new_competitions_list():
    try:
        api = KaggleApi()
        api.authenticate()

        competitions_list = []
        for info in api.competitions_list():
            start_date = getattr(info, 'enabledDate')

            # assume to run once a day
            pre_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)

            if start_date >= pre_date:
                competitions_list.append(info)
        return competitions_list

    except Exception as e:
        logger.error(e)


def get_progress_competitions_list():
    try:
        api = KaggleApi()
        api.authenticate()

        competitions_list = []
        for info in api.competitions_list():
            end_date = getattr(info, 'deadline')

            # assume to run once a day
            now_date = datetime.datetime.utcnow()

            if end_date >= now_date:
                competitions_list.append(info)
        return competitions_list

    except Exception as e:
        logger.error(e)


def create_event(competition):
    calendar_list = get_calendar_list(competition)

    for calendar_name in calendar_list:
        competition_name = getattr(competition, 'title')
        calendar_json = open_json('calendar.json')
        calendar_id = calendar_json[calendar_name]['id']
        body = get_calendar_body(competition, calendar_name)

        try:
            service = new_calendar_service()
            event = service.events().insert(calendarId=calendar_id, body=body).execute()

            msg = 'Create event. calendar id: {}, competitions name: {}'.format(
                calendar_id, competition_name)
            logger.debug(msg)

        except Exception as e:
            logger.error('{}: {}\n{}'.format(calendar_name, body, e))


def get_calendar_list(info):
    calendar_json = open_json('calendar.json')

    calendar_list = [calendar_json['all']['name']]

    awards_points = getattr(info, 'awardsPoints')
    if awards_points:
        calendar_list.append(calendar_json['awards_points']['name'])
    else:
        return calendar_list

    # Class Tag convert to str
    tags = [str(tag) for tag in getattr(info, 'tags')]

    # tabular / text / image
    is_etc_data = True
    for calendar in calendar_json:
        if calendar_json[calendar]['data'] in tags:
            calendar_list.append(calendar_json[calendar]['name'])
            is_etc_data = False

    if is_etc_data:
        calendar_list.append(calendar_json['etc']['name'])

    return calendar_list


def get_calendar_body(competition_info, calendar_name):
    summary = getattr(competition_info, 'title')

    description = getattr(competition_info, 'url')
    description = description.replace(':80', '')

    start_date = getattr(competition_info, 'enabledDate')
    start_date = start_date.isoformat()

    end_date = getattr(competition_info, 'deadline')
    end_date = end_date.isoformat()

    # Different colors depending on whether there is awards points
    calendar_json = open_json('calendar.json')
    if getattr(competition_info, 'awardsPoints'):
        color_id = calendar_json[calendar_name]['colorId_1']
    else:
        color_id = calendar_json[calendar_name]['colorId_2']

    body = open_json('calendar_format.json')

    body['summary'] = summary
    body['description'] = description
    body['start']['dateTime'] = start_date
    body['end']['dateTime'] = end_date
    body['colorId'] = color_id

    return body


def delete_all_event(calendar_id):
    try:
        service = new_calendar_service()
        result = service.events().list(calendarId=calendar_id).execute()
        for event in result['items']:
            result = service.events().delete(
                calendarId=calendar_id, eventId=event['id']).execute()
        logger.debug('delete: {}'.format(event['id']))
    except Exception as e:
        logger.error('{}: {}'.format(calendar_id, e))


if __name__ == "__main__":
    # If you run for the first time, run this function
    # competitions_list = get_progress_competitions_list()
    competitions_list = get_new_competitions_list()

    for competition in competitions_list:
        create_event(competition)
