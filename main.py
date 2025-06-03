import telebot
import os
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

debtors = {}

def add_debtor(username):
    if username not in debtors:
        debt = random.randint(1000, 10_000_000)
        debtors[username] = debt
        return debt
    return None

@bot.message_handler(commands=['инициализация'])
def init_debtors(message):
    """Записывает всех админов как должников"""
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "Эта команда работает только в группах.")
        return

    admins = bot.get_chat_administrators(message.chat.id)
    added = []
    for admin in admins:
        username = admin.user.username or admin.user.first_name
        debt = add_debtor(username)
        if debt:
            added.append(f"@{username} теперь должен {debt:,}₽")

    if added:
        bot.send_message(message.chat.id, "\n".join(added))
    else:
        bot.send_message(message.chat.id, "Все уже были в списке должников.")

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_members(message):
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

bot.polling()
