import datetime
import json
import os
import requests
from kaggle.api.kaggle_api_extended import KaggleApi
from pytz import timezone
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client

CALENDER_SCOPES = 'https://www.googleapis.com/auth/calendar'
CALENDER_ID = 'fernk4og93701fo005rgp2kea4@group.calendar.google.com'


import google.auth
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
CONTENTS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
flow = InstalledAppFlow.from_client_config(client_config=CONTENTS, scopes=CALENDER_SCOPES)
CREDS = flow.run_local_server()
SERVICE = build('calendar', 'v3', http=CREDS.authorize(Http()))

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']


def get_competitions_list(category='featured'):
    api = KaggleApi()
    api.authenticate()
    return api.competitions_list(category=category)


def get_event_name_list():
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = SERVICE.events().list(
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

        # 新規コンペの場合にイベントを作成
        # 開催中のコンペのみ作成
        # 作成に成功した場合は Slack に通知
        if competition_name not in event_name_list and now < end_date:
            key_list = ['url']
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
            event = SERVICE.events().insert(calendarId=CALENDER_ID, body=body).execute()

            competition_url = getattr(competition_info, 'url')
            post_slack(competition_name, competition_url)


def post_slack(competition_name, competition_url):
    payload = {
        'username': 'Kaggle Competitions Calender',
        'icon_url': 'https://pbs.twimg.com/profile_images/1146317507/twitter_400x400.png',
        'attachments': [{
            'fallback': 'Competition Launch',
            'color': '#D00000',
            'fields': [{
                'title': competition_name,
                'value': competition_url,
            }]
        }]
    }
    requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))


def main():
    competitions_list = get_competitions_list()
    create_events(competitions_list)


main()
