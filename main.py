import os

from kaggle.api.kaggle_api_extended import KaggleApi

import datetime
from pytz import timezone
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

CALENDER_SCOPES = 'https://www.googleapis.com/auth/calendar'
CALENDER_ID = 'fernk4og93701fo005rgp2kea4@group.calendar.google.com'


# store = file.Storage('credentials/token.json')
# creds = store.get()
# if not creds or creds.invalid:
#     flow = client.flow_from_clientsecrets(
#         'credentials/credentials.json', CALENDER_SCOPES)
#     creds = tools.run_flow(flow, store)
store = file.Storage('credentials/token.json')
creds = store.get()
service = build('calendar', 'v3', http=creds.authorize(Http()))


def get_competitions_list(category='featured'):
    api = KaggleApi()
    api.authenticate()
    return api.competitions_list(category=category)


def get_event_name_list():
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId=CALENDER_ID, timeMin=now).execute()
    events = events_result.get('items', [])

    events_name = []
    for event in events:
        events_name.append(event['summary'])

    return events_name


def create_events(competitions_list):
    event_name_list = get_event_name_list()
    if event_name_list is None:
        return 0

    for competition_info in competitions_list:
        competition_name = getattr(competition_info, 'title')

        now = datetime.datetime.utcnow().isoformat()

        end_date = getattr(competition_info, 'deadline')
        end_date = timezone('UTC').localize(end_date)
        end_date = end_date.isoformat()

        # 新規コンペの場合
        if competition_name not in event_name_list and now < end_date:
            key_list = ['description', 'evaluationMetric',
                        'isKernelsSubmissionsOnly', 'tags', 'url']
            description = ''
            for key in dir(competition_info):
                if key in key_list:
                    description += '{}: {}\n'.format(key,
                                                     getattr(competition_info, key))

            start_date = getattr(competition_info, 'enabledDate')
            start_date = timezone('UTC').localize(start_date)
            start_date = start_date.isoformat()

            body = {
                'summary': competition_name,
                'description': description,
                'start': {
                    'dateTime': start_date,
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': end_date,
                    'timeZone': 'America/Los_Angeles',
                },
                'reminders': {
                    'useDefault': False,
                },
                'visibility': 'public',
            }
            event = service.events().insert(calendarId=CALENDER_ID, body=body).execute()
            print('[Create] {}'.format(competition_name))


def main():
    competitions_list = get_competitions_list()
    create_events(competitions_list)


main()
