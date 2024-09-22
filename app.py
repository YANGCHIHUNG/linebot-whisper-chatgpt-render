from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

app = Flask(__name__)

# OpenAI API 金鑰
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# LINE Bot 的 channel secret 和 access token
line_bot_api = "jEev/GLvPZYSbP7yWaLN9WRSNPgp/Onpw6vzMzRjdYUvrjJ7fDa81D/+laXdw3qUJHuQjy2w+nbF8O6Sz0ADoBR5q2W0ARJu57OjqKMuwyAZmfcg+1Tn1z0lmaNA3UAHMCNcAh2c9/bT+2wxuL8JlQdB04t89/1O/w1cDnyilFU="
handler = WebhookHandler("9af683a43efbca81a89a8f849e53687a")

# Webhook 路由
@app.route("/webhook", methods=['POST'])
def webhook():
    # 取得 X-Line-Signature header 值
    signature = request.headers['X-Line-Signature']

    # 確認此請求來自 LINE 伺服器
    body = request.get_data(as_text=True)
    print(f"Received webhook body: {body}")  # 打印接收到的 webhook 資訊
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 取得使用者輸入的文字
    user_message = event.message.text
    print(f"Received message from user: {user_message}")  # 打印使用者訊息

    # 立即回覆「已收到」訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="已收到")
    )
    print("Replied with acknowledgment: 已收到")  # 打印已回覆訊息

    # 呼叫 ChatGPT 進行摘要
    summary = summarize_with_chatgpt(user_message)

    # 回傳 ChatGPT 生成的摘要給使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=summary)
    )
    print(f"Replied with summary: {summary}")  # 打印 ChatGPT 的摘要結果

def summarize_with_chatgpt(text):
    """
    呼叫 OpenAI 的 ChatGPT 模型，生成文字摘要
    """
    print(f"Sending message to ChatGPT for summarization: {text}")  # 打印送出的訊息

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個摘要助手"},
                {"role": "user", "content": text},
            ]
        )
        summary = response['choices'][0]['message']['content'].strip()
        print(f"Received summary from ChatGPT: {summary}")  # 打印 ChatGPT 回傳的摘要
        return summary

    except Exception as e:
        print(f"Error during ChatGPT summarization: {e}")  # 打印錯誤訊息
        return "抱歉，摘要生成失敗，請稍後再試。"

if __name__ == "__main__":
    print("Starting app...")  # 打印應用啟動訊息
    app.run()
