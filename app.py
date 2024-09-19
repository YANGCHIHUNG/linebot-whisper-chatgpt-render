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

if __name__ == "__main__":
    app.run(port=8000)
