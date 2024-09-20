'''
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, AudioMessage, TextSendMessage
import os
import openai

app = Flask(__name__)

# Line Bot API credentials
line_bot_api = LineBotApi('jEev/GLvPZYSbP7yWaLN9WRSNPgp/Onpw6vzMzRjdYUvrjJ7fDa81D/+laXdw3qUJHuQjy2w+nbF8O6Sz0ADoBR5q2W0ARJu57OjqKMuwyAZmfcg+1Tn1z0lmaNA3UAHMCNcAh2c9/bT+2wxuL8JlQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9af683a43efbca81a89a8f849e53687a')

# OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'



# Function to summarize text using OpenAI (ChatGPT)
def summarize_highlight(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize the key points of the following lecture:\n\n{text}",
        max_tokens=150,
        temperature=0.7
    )
    summary = response['choices'][0]['text'].strip()
    return summary

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Handle audio messages
@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    # Get the audio message content
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    # Save the audio file locally
    audio_file_path = "input.mp3"
    with open(audio_file_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # Transcribe the audio to text
    transcribed_text = transcribe_audio_to_text(audio_file_path)

    # Summarize the transcribed text
    summarized_text = summarize_highlight(transcribed_text)

    # Reply with the summary
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=summarized_text)
    )

if __name__ == "__main__":
    app.run()


from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, AudioMessage, TextSendMessage
import os
import whisper
import openai

app = Flask(__name__)

# Line Bot API credentials
line_bot_api = LineBotApi('jEev/GLvPZYSbP7yWaLN9WRSNPgp/Onpw6vzMzRjdYUvrjJ7fDa81D/+laXdw3qUJHuQjy2w+nbF8O6Sz0ADoBR5q2W0ARJu57OjqKMuwyAZmfcg+1Tn1z0lmaNA3UAHMCNcAh2c9/bT+2wxuL8JlQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9af683a43efbca81a89a8f849e53687a')


# OpenAI API key (for ChatGPT)
openai.api_key = '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'

# Load Whisper model (you can choose 'base', 'small', 'medium', or 'large' depending on your needs)
model = whisper.load_model("base")

# Function to transcribe audio using Whisper
def transcribe_audio_to_text(file_path):
    result = model.transcribe(file_path)
    return result['text']

# Function to summarize text using OpenAI's ChatGPT
def summarize_text(text):
    response = openai.Completion.create(
        engine="text-davinci-003",  # ChatGPT's underlying engine
        prompt=f"Summarize the key points of the following text:\n\n{text}",
        max_tokens=150,
        temperature=0.7
    )
    summary = response.choices[0].text.strip()
    return summary

@app.route("/callback", methods=['POST'])
def callback():
    # Line signature verification
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Handle audio messages
@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    # Get the audio message content (MP3)
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    # Save the audio file locally
    audio_file_path = "input.mp3"
    with open(audio_file_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # Transcribe the audio to text using Whisper
    transcribed_text = transcribe_audio_to_text(audio_file_path)

    # Summarize the transcribed text using ChatGPT
    summarized_text = summarize_text(transcribed_text)

    # Send the summarized text back to the user in the Line Bot
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=summarized_text)
    )
*/

if __name__ == "__main__":
    app.run(port=8000)

'''
import os
from flask import Flask, request, jsonify
import requests
import openai

# 初始化 Flask 应用
app = Flask(__name__)

# 设置 Line 和 OpenAI 的密钥（从环境变量获取）
LINE_ACCESS_TOKEN = os.getenv('jEev/GLvPZYSbP7yWaLN9WRSNPgp/Onpw6vzMzRjdYUvrjJ7fDa81D/+laXdw3qUJHuQjy2w+nbF8O6Sz0ADoBR5q2W0ARJu57OjqKMuwyAZmfcg+1Tn1z0lmaNA3UAHMCNcAh2c9/bT+2wxuL8JlQdB04t89/1O/w1cDnyilFU=')
handler = os.getenv('9af683a43efbca81a89a8f849e53687a')
openai.api_key = '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'

# Line Messaging API 的请求头
headers = {
    "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# 处理 Line Bot Webhook 的消息
@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    events = body.get("events", [])
    
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "audio":
            # 获取音频消息ID
            message_id = event["message"]["id"]
            
            # 调用 Line API 下载音频文件
            audio_content = download_line_audio(message_id)

            if audio_content:
                # 保存音频文件
                with open("audio_file.m4a", "wb") as f:
                    f.write(audio_content)

                # 使用 Whisper API 进行转录
                transcription = transcribe_audio_with_whisper("audio_file.m4a")

                # 使用 ChatGPT 将转录文本整理为重点
                summary = summarize_with_chatgpt(transcription)

                # 回复用户处理结果
                reply_to_line(event["replyToken"], summary)
    
    return "OK", 200

# 下载 Line 音频消息
def download_line_audio(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    response = requests.get(url, headers={"Authorization": f"Bearer {LINE_ACCESS_TOKEN}"})
    
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to download audio:", response.status_code)
        return None

# 调用 Whisper API 转录音频
def transcribe_audio_with_whisper(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    response = openai.Audio.transcribe(model="whisper-1", file=audio_file)
    transcription = response["text"]
    audio_file.close()
    return transcription

# 调用 ChatGPT API 进行摘要生成
def summarize_with_chatgpt(text):
    prompt = f"请将以下内容整理成重点：\n\n{text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一名优秀的文本摘要专家。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    summary = response["choices"][0]["message"]["content"]
    return summary

# 向用户发送 Line 消息回复
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
        print("Failed to send reply:", response.status_code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

