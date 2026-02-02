import telebot
import requests
import os

bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
API_URL = "https://ai-toxicityblock-and-cyberbullying.onrender.com/api/detect"

@bot.message_handler(func=lambda m: True)
def check_toxic(message):
    if message.from_user.is_bot or not message.text: return
    resp = requests.post(API_URL, json={"text": message.text})
    if resp.json().get('toxic'):
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, f"🚫 {message.from_user.first_name} blocked:\n\"{message.text}\"")
        
bot.polling(none_stop=True)
