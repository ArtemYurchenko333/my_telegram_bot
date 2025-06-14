import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я простой эхо-бот.",
        #reply_markup=ForceReply(selective=True), # Закомментировано, если не нужно
    )

# Обработчик текстовых сообщений (эхо)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

def main() -> None:
    """Запускает бота."""
    # Получаем токен бота из переменной окружения
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set.")
        raise ValueError("BOT_TOKEN environment variable is required.")

    # Создаем приложение и передаем токен бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Добавляем обработчик для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    # В Render мы будем использовать webhook, но для локального тестирования можно использовать polling
    # Для развертывания на Render мы используем webhook
    PORT = int(os.environ.get("PORT", "8080")) # Render назначает порт
    WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME") # Render предоставляет hostname

    if WEBHOOK_URL:
        # Устанавливаем webhook
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN, # Путь для webhook, обычно токен
            webhook_url=f"https://{WEBHOOK_URL}/{BOT_TOKEN}"
        )
        logger.info(f"Webhook set to https://{WEBHOOK_URL}/{BOT_TOKEN}")
    else:
        # Для локального тестирования можно использовать polling
        logger.info("RENDER_EXTERNAL_HOSTNAME not found, running with polling (for local testing).")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()