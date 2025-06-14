import os
import logging
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

    # Render предоставляет EXTERNAL_HOSTNAME без порта (потому что он использует 443 по умолчанию)
    WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    if WEBHOOK_URL:
        # URL, который мы сообщаем Telegram API, должен быть HTTPS и не содержать порт
        # Render сам перенаправит 443 на ваш PORT
        webhook_telegram_url = f"https://{WEBHOOK_URL}/{BOT_TOKEN}"

        logger.info(f"Starting webhook on internal port {PORT} with path /{BOT_TOKEN}")
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN
        )

        logger.info(f"Setting Telegram webhook to: {webhook_telegram_url}")
        updater.bot.set_webhook(webhook_telegram_url) # Здесь не должно быть порта
    else:
        logger.info("RENDER_EXTERNAL_HOSTNAME not found, running with polling (for local testing).")
        updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()
