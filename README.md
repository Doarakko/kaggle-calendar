# [Kaggle Calendar](https://kaggle-calendar.herokuapp.com/)
[![CircleCI](https://circleci.com/gh/Doarakko/kaggle-calendar.svg?style=svg)](https://circleci.com/gh/Doarakko/kaggle-calendar)

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Requirements
- Python 3
- pip
- Kaggle API
- Google Calender API
- Heroku CLI
- Slack

## Directory structure
```
.
├── LICENSE
├── Procfile
├── README.md
├── calendar.json
├── config.py
├── credentials
│   └── token.json
├── format
│   ├── calendar_insert.json
│   └── slack_post.json
├── .kaggle
│   └── kaggle.json
├── main.py
├── package.json
├── public
│   ├── index.html
│   └── style.css
├── requirements.txt
├── runtime.txt
└── server.js
```

## Usage
### 1. Download code
```
$ git clone https://github.com/Doarakko/kaggle-calendar
$ cd kaggle-calendar
```
### 2. Install Python library
```
$ pip install -r requirements.txt
```
### 3. Run on local
#### 3.1 Change `main.py`
```
LOCAL = True
```
#### 3.2 Set credentials file
```
.
└── credentials
    └── token.json
```
- `config.py`
```
import os

os.environ['SLACK_WEBHOOK_URL'] = 'https://hooks.slack.com/services/<hoge>'
```
#### 3.3 Run
```
$ python main.py
$ open public/index.html
```
### 4. Run on Heroku
#### 4.1 Change `main.py`
```
LOCAL = False
```
#### 4.2 Deploy to Heroku
```
$ heroku login
$ heroku create <app name>
$ git add -A
$ git commit -m 'Hello World!'
$ git push heroku master
```
#### 4.3. Set config vars
Set config vars using Heroku CLI or Heroku Dashboard.

|Name|Note|
|:--|:--|
|GOOGLE_APPLICATION_CREDENTIALS|JSON format|
|KAGGLE_USERNAME||
|KAGGLE_KEY||
|SLACK_WEBHOOK_URL||
#### 4.4 Run
```
$ heroku run python main.py
```
Access to `https://<app name>.herokuapp.com`.
#### 4.5 Set scheduler
```
$ heroku addons:create scheduler:standard
```
Set task on Heroku Dashboard.
## Hints
- [Kaggle の Google Calendar を作りました](https://doarakko.hatenablog.com/entry/2018/12/25/200000)