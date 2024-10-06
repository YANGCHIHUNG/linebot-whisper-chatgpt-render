import os
import openai
import tempfile
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, AudioMessage, TextSendMessage

# 設定 OpenAI 的 API 金鑰
openai.api_key = os.getenv("OPENAI_API_KEY")

# 設定你的 LINE Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    # 取得語音檔案的URL
    message_content = line_bot_api.get_message_content(event.message.id)
    
    with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        temp_file_path = tf.name
    
    # 使用 OpenAI Whisper API 進行語音轉文字
    with open(temp_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
    # 回傳轉成的文字訊息給用戶
    text_message = TextSendMessage(text=transcript["text"])
    line_bot_api.reply_message(event.reply_token, text_message)
    
    # 刪除臨時文件
    os.remove(temp_file_path)

if __name__ == "__main__":
    app.run()
