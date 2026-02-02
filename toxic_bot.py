from flask import Flask
import telebot
import threading
import os
import requests

app = Flask(__name__)
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))

@app.route('/')
def home():
    return "Toxicity Bot + Web UI LIVE!"

@bot.message_handler(func=lambda m: True)
def check_toxic(message):
    if message.from_user.is_bot or not message.text: return
    try:
        resp = requests.post("https://ai-toxicityblock-and-cyberbullying.onrender.com/api/detect", 
                           json={"text": message.text}, timeout=5)
        if resp.status_code == 200 and resp.json().get('toxic'):
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"🚫 {message.from_user.first_name} blocked:\n\"{message.text}\"")
    except:
        pass

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
