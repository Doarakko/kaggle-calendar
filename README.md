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

## Usage
### Deploy to Heroku
#### 1. 
#### 2. Set scheduler
```
$ heroku addons:create scheduler:standard
```
Set task on Heroku Dashboard.

### Run on local
#### 1. Download code
```
$ git clone https://github.com/Doarakko/kaggle-calendar
$ cd kaggle-calendar
```
### 2. Install Python library
```
$ pip install -r requirements.txt
```
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

## Contribution
Welcome issue and pull request.

## License
MIT

## Author
Doarakko