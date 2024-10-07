import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FileMessage, TextSendMessage
from pydub import AudioSegment

app = Flask(__name__)

# 設定你的 LINE Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
WHISPER_API_MAX_SIZE = 25 * 1024 * 1024  # Whisper API 限制 25MB

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

# 將音檔切割為較小的片段（每片段 10 分鐘）
def split_audio(file_path, segment_length_ms=300000):
    audio = AudioSegment.from_file(file_path)
    duration_ms = len(audio)
    
    audio_segments = []
    for i in range(0, duration_ms, segment_length_ms):
        segment = audio[i:i+segment_length_ms]
        segment_path = f"{file_path}_part_{i // segment_length_ms}.m4a"
        segment.export(segment_path, format="m4a")
        audio_segments.append(segment_path)
    
    return audio_segments

# 將音檔發送給 Whisper API 進行語音轉文字
def transcribe_audio(file_path):
    with open(file_path, 'rb') as audio_file:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }
        files = {
            'file': (file_path, audio_file, 'audio/m4a')
        }
        data = {
            'model': 'whisper-1',
            'language': 'zh'
        }
        response = requests.post(WHISPER_API_URL, headers=headers, files=files, data=data)
        
    if response.status_code == 200:
        return response.json().get('text')
    else:
        print(f"Error in Whisper transcription: {response.text}")
        return ""

# 使用 ChatGPT 彙整重點
def summarize_text(text):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': '你是一個幫助將長篇文章進行重點彙整的助手。'},
            {'role': 'user', 'content': f'請幫我彙整以下內容的重點：{text}'}
        ],
        'temperature': 0.7
    }
    
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Error in ChatGPT summarization: {response.text}")
        return "無法彙整重點"

# 處理接收到的檔案訊息
@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    # 儲存檔案
    audio_file_path = f"{message_id}.m4a"
    with open(audio_file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    
    # 檢查檔案大小
    file_size = os.path.getsize(audio_file_path)
    if file_size > WHISPER_API_MAX_SIZE:
        # 如果檔案太大，進行分割
        audio_segments = split_audio(audio_file_path)
    else:
        # 否則直接處理整個音檔
        audio_segments = [audio_file_path]
    
    # 將分割後的每個片段進行轉錄
    all_text = ""
    for segment in audio_segments:
        transcription = transcribe_audio(segment)
        all_text += transcription + "\n"

    # 將轉錄結果作為文字訊息回傳給用戶
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"語音轉文字結果：\n{all_text}")
    )
    
    # 使用 ChatGPT 彙整重點
    summary = summarize_text(all_text)
    
    # 回傳彙整的重點
    line_bot_api.push_message(
        event.source.user_id,
        TextSendMessage(text=summary)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
