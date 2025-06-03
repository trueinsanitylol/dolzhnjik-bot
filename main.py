import telebot
import os
import random
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

debtors = {}

def add_debtor(username):
    if username not in debtors:
        debt = random.randint(1000, 10_000_000)
        debtors[username] = debt
        return debt
    return None

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    for user in message.new_chat_members:
        username = user.username or user.first_name
        debt = add_debtor(username)
        if debt:
            bot.send_message(message.chat.id, f"@{username} теперь должен {debt:,}₽!")

@bot.message_handler(commands=['список'])
def show_debtors(message):
    if not debtors:
        bot.send_message(message.chat.id, "Список должников пуст.")
        return
    text = "💰 Должники:\n"
    for i, (name, amount) in enumerate(debtors.items(), 1):
        text += f"{i}. @{name} должен {amount:,}₽\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['удалить'])
def remove_debtor(message):
    try:
        username = message.text.split()[1].lstrip('@')
        if username in debtors:
            del debtors[username]
            bot.send_message(message.chat.id, f"@{username} больше не в долгах.")
        else:
            bot.send_message(message.chat.id, f"@{username} не найден.")
    except IndexError:
        bot.send_message(message.chat.id, "Напиши так: /удалить @username")

@bot.message_handler(commands=['добавить'])
def add_debtor_command(message):
    try:
        username = message.text.split()[1].lstrip('@')
        if username in debtors:
            bot.send_message(message.chat.id, f"@{username} уже в списке должников.")
        else:
            debt = add_debtor(username)
            bot.send_message(message.chat.id, f"@{username} теперь должен {debt:,}₽!")
    except IndexError:
        bot.send_message(message.chat.id, "Напиши так: /добавить @username")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    bot.remove_webhook()
    webhook_url = os.getenv("RENDER_EXTERNAL_URL") + "/" + TOKEN
    bot.set_webhook(url=webhook_url)
    return "Бот запущен!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
