from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set")

app = Flask(__name__)

telegram_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот-помощник 👋")

telegram_app.add_handler(CommandHandler("start", start))

# Инициализация приложения — вызывается один раз при старте сервера
async def initialize_bot():
    await telegram_app.initialize()
    await telegram_app.start()
    logging.info("Telegram bot initialized")

# Храним event loop и инициализируем заранее
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(initialize_bot())

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        # Telegram присылает JSON обновление
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        # Запускаем обработку обновления в уже инициализированном приложении
        loop.run_until_complete(telegram_app.process_update(update))
        return "OK"
    except Exception as e:
        logging.exception("Ошибка при обработке вебхука")
        return "Internal Server Error", 500

if __name__ == "__main__":
    # Запускаем Flask на порту 5000
    app.run(host="0.0.0.0", port=5000)
