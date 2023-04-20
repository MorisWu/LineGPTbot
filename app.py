import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort
import openai

LINE_CHANNEL_ACCESS_TOKEN = 'Your LINE CHANNEL ACCESS TOKEN'
LINE_CHANNEL_SECRET = 'Your LINE CHANNEL SECRET'
OPENAI_API_KEY = 'Your OpenAI API key'

# 初始化Line Bot API
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化OpenAI API
openai.api_key = OPENAI_API_KEY

user_dict = {}

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    # 確認請求是否來自 Line 平臺
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if not event.source.user_id in user_dict:
        print('add: ' + event.source.user_id)
        user_dict[event.source.user_id] = {}
        user_dict[event.source.user_id]['message'] = []
        user_displayname = line_bot_api.get_profile(event.source.user_id).display_name
        user_dict[event.source.user_id]['display_name'] = user_displayname


    user_dict[event.source.user_id]['message'].append({"role": "user", "content": "盡量簡短但不要太簡短的回應以下句子："+event.message.text})

    # 使用OpenAI API產生回覆訊息
    response = openai.ChatCompletion.create(model= "gpt-3.5-turbo",
                                            messages=user_dict[event.source.user_id]['message'],
                                            n=1,
                                            max_tokens=300,
                                            stop=None,
                                            temperature=0.5)

    # 使用Line Bot API回復使用者的訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response['choices'][0]['message']['content'])
    )
    user_dict[event.source.user_id]['message'].append({"role": "assistant", "content": response['choices'][0]['message']['content']})

    if len(user_dict[event.source.user_id]['message']) > 8:
        for i in range(2):
            user_dict[event.source.user_id]['message'].remove(user_dict[event.source.user_id]['message'][i])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 50))
    app.run(host="0.0.0.0", port=port)