import os
from flask import Flask, request, abort, send_file
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, AudioMessage, TextSendMessage

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
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

# 處理接收到的音訊訊息
@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    # 取得音訊檔案的ID
    message_id = event.message.id
    
    # 將音訊檔案從LINE伺服器下載
    message_content = line_bot_api.get_message_content(message_id)
    
    # 儲存音訊檔案
    audio_file_path = f"{message_id}.m4a"
    with open(audio_file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    
    # 回傳已接收到的音訊檔案
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="音訊檔案已接收並將回傳給您。")
    )
    
    # 發送回音訊檔案
    with open(audio_file_path, 'rb') as f:
        line_bot_api.push_message(
            event.source.user_id,
            AudioSendMessage(original_content_url=f'https://your-domain/{audio_file_path}', duration=60000)  # 假設檔案時長為60秒
        )

@app.route('/<filename>', methods=['GET'])
def serve_audio_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
