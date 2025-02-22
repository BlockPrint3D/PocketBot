import telebot

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

updates = bot.get_updates()
for update in updates:
    print(update.message.chat.id)  # This prints your chat ID
