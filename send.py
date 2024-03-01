#!/usr/bin/env python
# coding: utf-8

# In[1]:


##Webhookが有効になっているか、URLが間違っていないかを確認する
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import psycopg2
import os

app = Flask(__name__)

# LINE Botのアクセストークン
CHANNEL_ACCESS_TOKEN = "S7+0uRSDDcMODsSGZxla3BWU2uf0B4/qWFVssztQT3bDxxEDSUd16zg0DnUVh7v6ngoNRY3E26NDoa3kNGcNVCVKqO2kVSxlq0s1OIb8T1RDQHAtJp145gqAFHTN9gdM9kUl0xCfPAPht9tzuGZwlgdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "c622d92bb84e3c7cbf09bda94a23cf1c"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

DATABASE_URL = os.environ['DATABASE_URL']

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text

    if 'を登録' in message_text: # メッセージが'と登録する'を含む場合
        keyword = message_text.replace('を登録', '') # キーワードを抽出
        store_in_database(user_id, keyword) # データベースに保存
    elif 'を削除' in message_text: # メッセージが'を削除'を含む場合
        keyword = message_text.replace('を削除', '') # キーワードを抽出
        delete_from_database(user_id, keyword) # データベースから削除
    elif '確認' in message_text: # メッセージが'確認'を含む場合
        keywords = fetch_from_database(user_id) # データベースから取得
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=', '.join(keywords)))

def store_in_database(user_id, keyword):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # ユーザーIDとキーワードをデータベースに保存
    cur.execute("INSERT INTO user_keywords (user_id, keyword) VALUES (%s, %s)", (user_id, keyword))

    conn.commit()
    cur.close()
    conn.close()

def delete_from_database(user_id, keyword):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # ユーザーIDとキーワードに一致するデータをデータベースから削除
    cur.execute("DELETE FROM user_keywords WHERE user_id = %s AND keyword = %s", (user_id, keyword))

    conn.commit()
    cur.close()
    conn.close()

def fetch_from_database(user_id):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # ユーザーIDに一致するキーワードをデータベースから取得
    cur.execute("SELECT keyword FROM user_keywords WHERE user_id = %s", (user_id,))

    keywords = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return keywords

if __name__ == "__main__":
    app.run()


# In[ ]:




