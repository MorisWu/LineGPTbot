from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('giz4GEgHUsXPauBPJBWB1LzyxUwO8d+HyDr4zASK7vBe2/LAElviZ+3IIFc5M2WOSVsdtX/3g1uE6vkr7f/pbMM/Iyk33RMBcPpfB05qGSfEDL2wCQEpwwJq7jWFhuZobxwLT6g8pyk+kumwhlBIsgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('7485e6889f5ff6e7a769f74d347dc2ad')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
