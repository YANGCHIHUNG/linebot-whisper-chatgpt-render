import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FileMessage, TextSendMessage

app = Flask(__name__)

# 設定你的 LINE Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Webhook 接收請求
@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    print("Received webhook: ", body)  # 確認 webhook 被觸發
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Check the channel secret.")
        abort(400)
    
    return 'OK'

# 處理接收到的檔案訊息
@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    # 回傳已接收到的音檔訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="已收到您的音檔。")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
