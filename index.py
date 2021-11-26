from dotenv import load_dotenv
import os

from flask import Flask, Response, request, session

from chefbot import ask, append_interaction_to_chat_log

import telebot

load_dotenv()

# logger = telebot.logger
# telebot.logger.setLevel(logging.INFO)

TOKEN = os.environ.get('TELEGRAM_KEY')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# if for some reason, your conversation with the chef gets weird, change the secret key 
app.config['SECRET_KEY'] = 'top-NSFJSFDKFjkfsk!'

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)

@bot.callback_query_handler(func=lambda call: True)
def test_callback(call): # <- passes a CallbackQuery type object to your function
    logger.info(call)

@bot.message_handler(func=lambda message: False, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def process_message(message):

    incoming_msg = message
    chat_log = session.get('chat_log')
    answer = ask(incoming_msg, chat_log)
    session['chat_log'] = append_interaction_to_chat_log(incoming_msg, answer, chat_log)
    print("the session chat_log = ", chat_log)

    bot.reply_to(message, answer)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://chefbot-caffeinum.vercel.app/' + TOKEN)
    return Response("<p>Webhook updated: /%s</p>" % ('https://chefbot-caffeinum.vercel.app/' + TOKEN), mimetype="text/html")
    # return "!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
