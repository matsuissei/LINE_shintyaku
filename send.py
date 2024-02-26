#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##HerokuにDATABASEURLとチャンネルアクセストークンを登録する
from datetime import datetime
import os
import psycopg2
from linebot import LineBotApi
from linebot.models import TextSendMessage
import requests

DATABASE_URL = os.environ['DATABASE_URL']
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

##keywordを引数に作品の情報を検索する
def append_message(keyword):
    
    # 日付
    now = datetime.now()

    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    
    yday = str(now.day + 1).zfill(2)
    
    protodate = year + "-" + month + "-" + day
    
    yes = year + "-" + month + "-" + yday
    nowdate = protodate + "T00:00:00"
    
    yesterday = yes + "T00:00:00"
    
    print(nowdate)
    
    URL ='https://api.dmm.com/affiliate/v3/ItemList?api_id=fwSE6apmeTUzewZuKc9m&affiliate_id=matsu55-994&service=digital&floor=videoa&site=FANZA&gte_date=' + nowdate + '&lte_date=' + yesterday + '&keyword=' + keyword
    
    response = requests.get(URL) 
    data = response.json()
    
    ##作品のタイトル、女優名、パッケージ、価格を検索
    title = data["result"]["items"][0]["title"]
    joyu = data["result"]["items"][0]["iteminfo"]["actress"][0]["name"]
    price = data["result"]["items"][0]["prices"]["price"]
    link = data["result"]["items"][0]["affiliateURL"]
     
    return title, joyu, price, link

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

cur.execute("SELECT user_id, keyword FROM user_keywords")
rows = cur.fetchall()

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

for row in rows:
    user_id = row[0]
    keyword = row[1]
    try:
        ##検索された情報から紹介文（massage）を生成
        tit, joy, pri, lin = append_message(keyword)
        text = "新しい作品があります！！！\n\n" + tit + "\n" + joy + "\n" + pri + "\n\n↓↓詳細はこちらから↓↓\n" + lin
        message = TextSendMessage(text=text)
        line_bot_api.push_message(user_id, message)
    except Exception as e:
        print(f"Error occurred: {e}")

cur.close()
conn.close()

