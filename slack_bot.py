import os

import openai
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests, json

load_dotenv(verbose=True)
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
openai.api_key = os.environ.get("OPENAI_API_KEY")
web_hook_url = os.environ.get("WEBHOOK_URL")

def respond_gpt(personality, input_text):
    client = openai.OpenAI(api_key = os.environ.get("OPEN_API_KEY"))
    response = client.chat.completions.create(
                   messages = [
                       {"role": "system", "content": personality},
                       {"role": "user", "content": input_text},
                   ],
                   #model = "gpt-3.5-turbo",
                   model = "gpt-4-turbo",
               )
    return response.choices[0].message.content

@app.event("app_mention")
def open_api_response(event, say):
    input_text = event["text"]
    thread_ts = event.get("thread_ts")
    ts = event["ts"]
    channel = event["channel"]

    personality = """
        あなたは Python プログラムの専門家です。
        Python プログラムに関しては公式のドキュメントや公式に近い情報源に基づいて回答してください。
        また Python プログラムに関する質問には回答だけでなく、それに関する解説や参考にすべきドキュメントやサンプルコードを示してください。
        それ以外の質問には普通に回答してください。
        """
    res_text = respond_gpt(personality, input_text)
    print(res_text)
    if thread_ts is not None:
        parent_thread_ts = event["thread_ts"]
        say(text = res_text, thread_ts = parent_thread_ts, channel=channel)
    else:
        say(text = res_text, channel=channel, thread_ts = ts)


@app.message("hello")
def message_hello(message, say):
   user = message['user']
   say(f"Hi there, <@{user}>!")
   requests.post(web_hook_url, data = json.dumps({
       'text': u'Notification from bolt_app.'
   }))

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
