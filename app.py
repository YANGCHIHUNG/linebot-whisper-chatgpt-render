import os
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 初始化 Flask 應用
app = Flask(__name__)

# Line Messaging API 的憑證
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# OpenAI API 憑證
openai.api_key = os.getenv('OPENAI_API_KEY')

# Line Webhook 接口
@app.route("/webhook", methods=['POST'])
def callback():
    # 獲取 Line 的簽名
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理來自 Line 的訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # 呼叫 OpenAI 的 ChatGPT API
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_message,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )

    chatgpt_response = response['choices'][0]['text'].strip()

    # 回應使用者的訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=chatgpt_response)
    )

# 啟動 Flask 伺服器
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
