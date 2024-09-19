from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# Line Bot API credentials
line_bot_api = LineBotApi('jEev/GLvPZYSbP7yWaLN9WRSNPgp/Onpw6vzMzRjdYUvrjJ7fDa81D/+laXdw3qUJHuQjy2w+nbF8O6Sz0ADoBR5q2W0ARJu57OjqKMuwyAZmfcg+1Tn1z0lmaNA3UAHMCNcAh2c9/bT+2wxuL8JlQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9af683a43efbca81a89a8f849e53687a')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"You said: {event.message.text}")
    )

if __name__ == "__main__":
    app.run()
