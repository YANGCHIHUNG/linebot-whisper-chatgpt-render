import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FileMessage, TextSendMessage

app = Flask(__name__)

# 設定你的 LINE Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
    # 取得音檔 ID 和名稱
    message_id = event.message.id
    file_name = event.message.file_name
    
    # 下載音檔
    message_content = line_bot_api.get_message_content(message_id)
    audio_file_path = f"/tmp/{file_name}"  # 假設使用 tmp 目錄來存儲檔案
    with open(audio_file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    
    # 調用 OpenAI Whisper API 進行語音轉文字
    transcription = transcribe_audio(audio_file_path)
    
    # 回傳轉換結果
    if transcription:
        result_text = transcription.get('text', '無法進行語音轉文字')
    else:
        result_text = '無法進行語音轉文字，請稍後再試。'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result_text)
    )

def transcribe_audio(file_path):
    """
    使用 OpenAI Whisper API 進行語音轉文字
    :param file_path: 儲存音檔的路徑
    :return: Whisper API 回傳的轉換結果
    """
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    with open(file_path, 'rb') as audio_file:
        files = {
            'file': (file_path, audio_file, 'audio/m4a'),
            'model': (None, 'whisper-1')
        }
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
