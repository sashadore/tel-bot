import os
import logging
import asyncio
import threading

from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не установлен")

app = Flask(__name__)

# Создаем приложение telegram бота (Application)
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот-помощник 👋")

telegram_app.add_handler(CommandHandler("start", start))

# Функция запуска event loop Telegram приложения в отдельном потоке
def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    logger.info("Запуск event loop Telegram приложения")
    loop.run_forever()

# Инициализируем telegram_app (создается event loop)
telegram_app.initialize()

# Запускаем event loop telegram_app в отдельном потоке
loop = asyncio.get_event_loop()
threading.Thread(target=start_event_loop, args=(loop,), daemon=True).start()

# Вебхук обработчик Flask
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    logger.info("Получен запрос от Telegram")
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    # Без блокировки ставим в очередь обработку обновления
    asyncio.run_coroutine_threadsafe(telegram_app.process_update(update), loop)
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Запуск Flask на порту {port}")
    app.run(host="0.0.0.0", port=port)
