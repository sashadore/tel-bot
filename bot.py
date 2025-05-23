import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Dispatcher

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Создаем приложение telegram-бота (dispatcher будет использоваться для обработки апдейтов)
application = ApplicationBuilder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-помощник с webhook.")

application.add_handler(CommandHandler("start", start))

# Функция для обработки входящих webhook запросов от Telegram
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return "OK"

# Запуск приложения Flask (Render запустит сам, здесь для локального теста)
if __name__ == "__main__":
    # Устанавливаем webhook у Telegram (один раз)
    bot.set_webhook(WEBHOOK_URL)
    app.run(port=5000)
