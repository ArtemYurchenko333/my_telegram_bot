import os
import logging
import time # Добавляем импорт time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я простой эхо-бот."
    )

# Обработчик текстовых сообщений (эхо)
async def echo(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(update.message.text)

def main() -> None:
    """Запускает бота."""
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set.")
        raise ValueError("BOT_TOKEN environment variable is required.")

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    PORT = int(os.environ.get("PORT", "8080")) # Это внутренний порт для Render

    WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    if WEBHOOK_URL:
        logger.info(f"RENDER_EXTERNAL_HOSTNAME received: {WEBHOOK_URL}")

        if ':' in WEBHOOK_URL:
            domain_only = WEBHOOK_URL.split(':')[0]
            logger.warning(f"Port detected in RENDER_EXTERNAL_HOSTNAME ({WEBHOOK_URL}). Using domain only: {domain_only}")
            WEBHOOK_URL = domain_only

        webhook_telegram_url = f"https://{WEBHOOK_URL}/{BOT_TOKEN}"

        logger.info(f"Final webhook URL to set in Telegram: {webhook_telegram_url}")
        logger.info(f"Attempting to start webhook listener on internal port {PORT} with path /{BOT_TOKEN}")

        try:
            updater.start_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=BOT_TOKEN
            )
            logger.info(f"Webhook listener started on port {PORT}.")
            # Даем серверу немного времени на старт
            time.sleep(1)
            
            logger.info(f"Setting Telegram webhook to: {webhook_telegram_url}")
            updater.bot.set_webhook(webhook_telegram_url)
            logger.info(f"Webhook set successfully to {webhook_telegram_url}")

        except Exception as e:
            logger.error(f"Error during webhook setup: {e}")
            # Добавим задержку, чтобы можно было увидеть ошибку перед выходом
            time.sleep(5)
            raise # Перевыбрасываем ошибку, чтобы Render её увидел
    else:
        logger.info("RENDER_EXTERNAL_HOSTNAME not found, running with polling (for local testing).")
        updater.start_polling()

    logger.info("Bot is now idling. Waiting for updates.")
    updater.idle() # Этот метод блокирует выполнение и держит бота активным

if __name__ == "__main__":
    main()
