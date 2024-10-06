from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import openai

# 初始化 Flask 應用
app = Flask(__name__)

# Line Bot Credentials
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# OpenAI API 憑證
openai.api_key = os.getenv('OPENAI_API_KEY')

# Line Webhook 接口
@app.route("/webhook", methods=['POST'])
def callback():
    # 獲取 Line 的簽名
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print(f"Error handling message: {e}")
        abort(500)
        
    return 'OK', 200

# 當接收到語音訊息時
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.content_provider.type == 'line':
        # 下載語音訊息
        message_content = line_bot_api.get_message_content(event.message.id)
        audio_path = f"{event.message.id}.mp3"

        print(f"Downloading audio to {audio_path}...")  # 除錯訊息

        with open(audio_path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)

        print("Audio downloaded successfully.")  # 除錯訊息
        
        # 使用 OpenAI Whisper API 進行語音轉文字
        transcription = transcribe_audio_openai(audio_path)

        print(f"Transcription: {transcription}")  # 除錯訊息，顯示轉錄的結果

        # 回傳轉錄結果給使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"語音轉錄結果：{transcription}")
        )

        # 回傳重點整理給使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=summary)
        )        

        # 呼叫 OpenAI API 來彙整重點
        summary = summarize_text(transcription)
        


        # 刪除暫時儲存的音檔
        os.remove(audio_path)
        print(f"Temporary audio file {audio_path} deleted.")  # 除錯訊息

def transcribe_audio_openai(audio_path):
    print(f"Uploading audio {audio_path} to OpenAI Whisper API...")  # 除錯訊息
    with open(audio_path, "rb") as audio_file:
        try:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="zh"  # 指定語言為中文
            )
            print("Transcription successful.")  # 除錯訊息
            return transcript['text']
        except Exception as e:
            print(f"Error during transcription: {e}")  # 除錯訊息
            return "轉錄過程中發生錯誤。"

def summarize_text(text):
    # 使用 ChatGPT 模型來彙整文字
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",  # 使用你偏好的模型版本
        prompt=f"請將以下文字彙整成重點:\n\n{text}",
        max_tokens=500,
        temperature=0.5,
        n=1,
        stop=None
    )
    return response['choices'][0]['text'].strip()


'''
# 處理來自 Line 的訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    try:
        # 呼叫 OpenAI 的 ChatGPT API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=150,
            n=1,
            temperature=0.7,
        )

        chatgpt_response = response['choices'][0]['message']['content'].strip()

        # 回應使用者的訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chatgpt_response)
        )
    except openai.error.RateLimitError:
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="目前服務暫時無法使用，請稍後再試。")
        )
    except Exception as e:
        print(f"Error handling message: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="發生了一個錯誤，請稍後再試。")
        )

'''



# 啟動 Flask 伺服器
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
