import os
import logging
import asyncio

from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN env variable is not set")

app = Flask(__name__)

telegram_app = ApplicationBuilder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Получена команда /start от пользователя {update.effective_user.id}")
    await update.message.reply_text("Привет! Я твой бот-помощник 👋")

telegram_app.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    logger.info("Получен запрос от Telegram")
    update_json = request.get_json(force=True)
    update = Update.de_json(update_json, telegram_app.bot)

    # Получаем event loop из telegram_app
    loop = telegram_app.updater._loop if hasattr(telegram_app, 'updater') else asyncio.get_event_loop()

    # Запускаем процессинг обновления синхронно
    try:
        loop.run_until_complete(telegram_app.process_update(update))
    except RuntimeError as e:
        # Если loop уже запущен (в случае reloader), создаём новый loop и запускаем в нём
        logger.warning(f"Основной цикл уже запущен: {e}, создаём новый цикл")
        new_loop = asyncio.new_event_loop()
        new_loop.run_until_complete(telegram_app.process_update(update))

    return "OK"

if __name__ == "__main__":
    logger.info("Инициализация Telegram приложения")
    telegram_app.initialize()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Запуск Flask на порту {port}")
    app.run(host="0.0.0.0", port=port)
