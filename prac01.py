# -*- coding: utf-8 -*-
from kaggle.api.kaggle_api_extended import KaggleApi

import gcalender_utility


# 以下週一で実行
# 1. コンペのリストをとってくる
# 2. すでにカレンダーに追加されているかチェック
# 3. あったら追加
#   - 予定名：コンペ名（competition_name）
#   - 説明欄: コンペのURL（competition_url）
# logger
# google calender作成utility
# google calender取得utility
# hoge

def get_competition_list():
    api = KaggleApi()
    api.authenticate()

    result = api.competitions_list()

    return result


def create_event(competition_list):
    """
    hige

    Parameters
    ----------
    competition_list : object
    """

    for competition_info in competition_list:
        category = getattr(competition_info, 'category')
        competition_name = getattr(competition_info, 'ref')

        if category == 'Featured' and not exists_gcalender(competition_name):
            competition_url = 'https://www.kaggle.com/c/' + competition_name
            deadline = getattr(competition_info, 'deadline')


def exists_gcalender(competition_name):
    print('hoge')


def main():
    competition_list = get_competition_list()
    create_event(competition_list)


main()
