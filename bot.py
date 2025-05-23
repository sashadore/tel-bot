from flask import Flask, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set. Please check your environment variables.")

app = Flask(__name__)

telegram_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот-помощник 👋")

telegram_app.add_handler(CommandHandler("start", start))

@app.route('/')
def index():
    return 'Бот работает!'

import logging

logging.basicConfig(level=logging.INFO)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    logging.info("Получен запрос от Telegram")
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        logging.info(f"Обновление от пользователя: {update.message.from_user.id}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(telegram_app.process_update(update))
        loop.close()

        logging.info("Обработка обновления успешна")
        return "OK"
    except Exception as e:
        logging.exception("Ошибка при обработке вебхука")
        return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(port=5000)
