import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set")

# Flask-приложение
app = Flask(__name__)

# Создаем Telegram Application (НЕ запускаем сразу)
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот-помощник 👋")

telegram_app.add_handler(CommandHandler("start", start))

# Асинхронный запуск и инициализация
init_started = False

async def ensure_bot_running():
    global init_started
    if not init_started:
        await telegram_app.initialize()
        await telegram_app.start()
        init_started = True

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    logger.info("Получен запрос от Telegram")
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)
        asyncio.run(handle_update(update))
    except Exception as e:
        logger.exception("Ошибка при обработке update")
    return "OK"

async def handle_update(update):
    await ensure_bot_running()
    await telegram_app.process_update(update)

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
