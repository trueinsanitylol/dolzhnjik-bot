import telebot
import os
import random


BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
debtors = {}

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    for user in message.new_chat_members:
        username = user.username or user.first_name
        if username not in debtors:
            debt = random.randint(1000, 10_000_000)
            debtors[username] = debt
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

bot.polling()
