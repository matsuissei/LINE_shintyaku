#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import os
import psycopg2
from linebot import LineBotApi
from linebot.models import TextSendMessage, TemplateSendMessage, ButtonsTemplate, URIAction
import requests

# 環境変数からデータベースURLとLINEチャンネルアクセストークンを取得
DATABASE_URL = os.environ['DATABASE_URL']
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

# keywordを引数に作品の情報を検索する関数
def append_message(keyword):
    # 日付の処理
    now = datetime.now()
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    yday = str(now.day - 1).zfill(2)  # 昨日の日付を取得するために1を引く
    
    protodate = year + "-" + month + "-" + day
    yes = year + "-" + month + "-" + yday
    nowdate = protodate + "T00:00:00"
    yesterday = yes + "T00:00:00"
    
    # DMM APIへのリクエストURL
    URL ='https://api.dmm.com/affiliate/v3/ItemList?api_id=fwSE6apmeTUzewZuKc9m&affiliate_id=matsu55-994&service=digital&floor=videoa&site=FANZA&gte_date=' + yesterday + '&lte_date=' + nowdate + '&keyword=' + keyword
    
    # DMM APIへのリクエスト送信
    response = requests.get(URL)
    data = response.json()
    
    # 作品のタイトル、女優名、パッケージ、価格を検索
    title = data["result"]["items"][0]["title"]
    link = data["result"]["items"][0]["affiliateURL"]
     
    return keyword, title, link

# メッセージを送信するメインの関数
def main():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    cur.execute("SELECT user_id, keyword FROM user_keywords")
    rows = cur.fetchall()
    
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

    for row in rows:
        user_id = row[0]
        keyword = row[1]
        try:
            keyword, title, link = append_message(keyword)
            message = TemplateSendMessage(
                alt_text='新しい作品情報',
                template=ButtonsTemplate(
                    title=f"【{keyword}】に関する新しい作品があります！",
                    text=title,
                    actions=[
                        URIAction(
                            label='詳細はこちら',
                            uri=link
                        )
                    ]
                )
            )
            line_bot_api.push_message(user_id, message)
        except Exception as e:
            print(f"Error occurred: {e}")

    cur.close()
    conn.close()

# スクリプトが直接実行された場合にmain関数を呼び出します
if __name__ == '__main__':
    main()