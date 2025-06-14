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

    WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    if WEBHOOK_URL:
        # Логируем то, что получаем от Render
        logger.info(f"RENDER_EXTERNAL_HOSTNAME received: {WEBHOOK_URL}")

        # Убедимся, что в WEBHOOK_URL нет порта. Если есть, удалим его.
        # Например, если WEBHOOK_URL стал 'my-bot.onrender.com:10000', мы это исправим.
        if ':' in WEBHOOK_URL:
            # Разделяем на домен и порт, берем только домен
            domain_only = WEBHOOK_URL.split(':')[0]
            logger.warning(f"Port detected in RENDER_EXTERNAL_HOSTNAME ({WEBHOOK_URL}). Using domain only: {domain_only}")
            WEBHOOK_URL = domain_only

        # URL, который мы сообщаем Telegram API, должен быть HTTPS и не содержать порт
        webhook_telegram_url = f"https://{WEBHOOK_URL}/{BOT_TOKEN}"

        logger.info(f"Final webhook URL to set in Telegram: {webhook_telegram_url}")

        logger.info(f"Starting webhook listener on internal port {PORT} with path /{BOT_TOKEN}")
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN
        )

        # Устанавливаем webhook
        updater.bot.set_webhook(webhook_telegram_url)
        logger.info(f"Webhook set successfully to {webhook_telegram_url}")
    else:
        logger.info("RENDER_EXTERNAL_HOSTNAME not found, running with polling (for local testing).")
        updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()
