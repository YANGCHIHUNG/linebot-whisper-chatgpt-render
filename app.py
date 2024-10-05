from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os
import openai
import whisper

# 初始化 Flask 應用
app = Flask(__name__)

# Line Messaging API 的憑證
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# OpenAI API 憑證
openai.api_key = os.getenv('OPENAI_API_KEY')

# Whisper 模型載入
model = whisper.load_model("base")  # 或 "small", "medium", "large" 根據你的需求


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
        
    return 'OK'

# 當接收到語音訊息時
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.content_provider.type == 'line':
        # 下載語音訊息
        message_content = line_bot_api.get_message_content(event.message.id)
        audio_path = f"{event.message.id}.mp3"
        with open(audio_path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        
        # 使用 Whisper 進行語音轉文字
        result = model.transcribe(audio_path, language="zh")
        transcription = result['text']

        # 呼叫 OpenAI API 來彙整重點
        summary = summarize_text(transcription)
        
        # 回傳重點整理給使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=summary)
        )

        # 刪除暫時儲存的音檔
        os.remove(audio_path)

def summarize_text(text):
    try:
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
