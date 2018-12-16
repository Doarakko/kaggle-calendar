import requests
import json

from kaggle.api.kaggle_api_extended import KaggleApi

import datetime
from pytz import timezone
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

CALENDER_SCOPES = 'https://www.googleapis.com/auth/calendar'
CALENDER_ID = 'rvilq00v5vsgdvpt5arso3d4m4@group.calendar.google.com'

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('./credentials.json', CALENDER_SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))


def get_competitions_list(category='featured'):
    api = KaggleApi()
    api.authenticate()
    return api.competitions_list(category=category)


def get_events_name():
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId=CALENDER_ID, timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    events_name = []
    for event in events:
        events_name.append(event['summary'])

    return events_name


def create_events(competitions_list):
    events_name = get_events_name()

    for competition_info in competitions_list:
        competition_name = getattr(competition_info, 'ref')

        # 新規コンペの場合
        if competition_name not in events_name:
            # 大会 URL
            competition_url = 'https://www.kaggle.com/c/' + competition_name

            # 開始日時
            start_date = getattr(competition_info, 'enabledDate')
            start_date = timezone('UTC').localize(start_date)
            start_date = start_date.isoformat()

            # 終了日時
            end_date = getattr(competition_info, 'deadline')
            end_date = timezone('UTC').localize(end_date)
            end_date = end_date.isoformat()

            body = {
                'summary': competition_name,
                'description': competition_url,
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


def main():
    competitions_list = get_competitions_list()
    create_events(competitions_list)


main()
