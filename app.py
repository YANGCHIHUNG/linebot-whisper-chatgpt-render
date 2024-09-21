import os
from flask import Flask, request, jsonify
from linebot import LineBotApi
from linebot.models import MessageEvent, AudioMessage
import requests
import openai

# 初始化 Flask 應用
app = Flask(__name__)

# 設定 Line 和 OpenAI 的密鑰（從環境變數中取得）
LINE_ACCESS_TOKEN = os.getenv("jEev/GLvPZYSbP7yWaLN9WRSNPgp/Onpw6vzMzRjdYUvrjJ7fDa81D/+laXdw3qUJHuQjy2w+nbF8O6Sz0ADoBR5q2W0ARJu57OjqKMuwyAZmfcg+1Tn1z0lmaNA3UAHMCNcAh2c9/bT+2wxuL8JlQdB04t89/1O/w1cDnyilFU=")
OPENAI_API_KEY = os.getenv("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")
openai.api_key = OPENAI_API_KEY

# Line Messaging API 的請求頭
headers = {
    "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# 處理 Line Bot Webhook 的消息
@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    events = body.get("events", [])
    print(f"Webhook received: {body}")  # 打印請求內容以進行調試
    
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "audio":
            # 取得音頻消息ID
            message_id = event["message"]["id"]
            
            # 調用 Line API 下載音頻檔案
            audio_content = download_line_audio(message_id)

            if audio_content:
                # 保存音頻檔案
                with open("audio_file.m4a", "wb") as f:
                    f.write(audio_content)

                # 使用 Whisper API 進行轉錄
                transcription = transcribe_audio_with_whisper("audio_file.m4a")

                # 使用 ChatGPT 將轉錄文本整理為重點
                summary = summarize_with_chatgpt(transcription)

                # 回覆用戶處理結果
                reply_to_line(event["replyToken"], summary)
    
    return "OK", 200

# 下載 Line 音頻消息
def download_line_audio(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    response = requests.get(url, headers={"Authorization": f"Bearer {LINE_ACCESS_TOKEN}"})
    
    if response.status_code == 200:
        return response.content
    else:
        print("下載音頻失敗:", response.status_code)
        return None

# 調用 Whisper API 轉錄音頻
def transcribe_audio_with_whisper(audio_file_path):
    try:
        audio_file = open(audio_file_path, "rb")
        response = openai.Audio.transcribe(model="whisper-1", file=audio_file)
        transcription = response["text"]
        print(f"Transcription result: {transcription}")
        audio_file.close()
        return transcription
    except Exception as e:
        print(f"Whisper API 轉錄失敗: {e}")
        return None


# 調用 ChatGPT API 進行摘要生成
def summarize_with_chatgpt(text):
    prompt = f"請將以下內容整理成重點：\n\n{text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一名優秀的文本摘要專家。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    summary = response["choices"][0]["message"]["content"]
    return summary

# 向用戶發送 Line 消息回覆
def reply_to_line(reply_token, message_text):
    payload = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": message_text
        }]
    }
    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=payload)
    
    if response.status_code != 200:
        print("回覆消息失敗:", response.status_code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
