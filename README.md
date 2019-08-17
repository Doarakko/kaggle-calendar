# [Kaggle Calendar](https://kaggle-calendar.herokuapp.com/)
Kaggle calendar using Kaggle API and Google Calendar API.

[![sample](https://doarakko.github.io/img/kaggle-calendar-sample.jpg)](https://kaggle-calendar.herokuapp.com/)

## Requirements
- Python 3.6
- pipenv
- Kaggle API
- Google Calendar API

## Usage
1. Clone code
```
$ git clone https://github.com/Doarakko/kaggle-calendar
$ cd kaggle-calendar
```

2. Install Python library
```
$ pipnv shell
```

3. Enter your environment variables
- `.env`
```
KAGGLE_KEY = abcdef
KAGGLE_USERNAME = john
GOOGLE_APPLICATION_CREDENTIALS = {
    "access_token": "gaerigae"
    ...
}
```
```
$ mv .env.example .env
```

- `calendar.json`

Enter your calendar id
```
{
    "all": {
        "id": "abcedfg@group.calendar.google.com",
        "name": "all",
        "data": null,
        "colorId_1": "1",
        "colorId_2": "2"
    },
    ...
```

4. Run on local
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