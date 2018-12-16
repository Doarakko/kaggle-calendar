import requests
import json

from kaggle.api.kaggle_api_extended import KaggleApi

import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

CALENDER_SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CALENDER_ID = 'rvilq00v5vsgdvpt5arso3d4m4@group.calendar.google.com'


def get_competitions_list(category='featured'):
    api = KaggleApi()
    api.authenticate()
    return api.competitions_list(category=category)


def get_events_name():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(
            './credentials.json', CALENDER_SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

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
            enabledDate = getattr(competition_info, 'enabledDate')
            # 終了日時
            deadline = getattr(competition_info, 'deadline')
            print(competition_name)


def main():
    competitions_list = get_competitions_list()
    create_events(competitions_list)


main()
