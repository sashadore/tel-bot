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

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# Получаем токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set")

# Создаём Flask-приложение
app = Flask(__name__)

# Создаём Telegram Application
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот-помощник 👋")

telegram_app.add_handler(CommandHandler("start", start))

# Инициализация Telegram Application (один раз при старте)
async def init_bot():
    await telegram_app.initialize()
    await telegram_app.start()

asyncio.run(init_bot())

# Обработка запросов от Telegram через вебхук
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    logger.info("Получен запрос от Telegram")

    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)
        asyncio.run(
