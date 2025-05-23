import os
import logging
import asyncio

from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set")

app = Flask(__name__)

# Создаём Telegram Application и инициализируем
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.initialize()  # Очень важно!

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот-помощник 👋")

telegram_app.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    logging.info("Получен запрос от Telegram")
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)

    loop = asyncio.get_event_loop()
    # Запускаем обработку в фоне, не блокируя Flask
    loop.create_task(telegram_app.process_update(update))

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Запуск Flask на порту {port}")
    app.run(host="0.0.0.0", port=port)
