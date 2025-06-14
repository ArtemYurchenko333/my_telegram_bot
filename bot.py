import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext # Изменения здесь!

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# logging.getLogger("httpx").setLevel(logging.WARNING) # Это не нужно для PTB < 20.x, использующего urllib3
logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None: # Изменения здесь!
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я простой эхо-бот."
    )

# Обработчик текстовых сообщений (эхо)
async def echo(update: Update, context: CallbackContext) -> None: # Изменения здесь!
    await update.message.reply_text(update.message.text)

def main() -> None:
    """Запускает бота."""
    # Получаем токен бота из переменной окружения
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set.")
        raise ValueError("BOT_TOKEN environment variable is required.")

    # Создаем Updater и передаем токен бота
    updater = Updater(BOT_TOKEN) # Изменения здесь!

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher # Изменения здесь!

    # Добавляем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))

    # Добавляем обработчик для текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo)) # Изменения здесь!

    # Запускаем бота
    PORT = int(os.environ.get("PORT", "8080")) # Render назначает порт
    WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME") # Render предоставляет hostname

    if WEBHOOK_URL:
        # Устанавливаем webhook
        # url_path для webhook в 13.x версии должен быть пустым или '/'
        # Полный URL для webhook
        webhook_url_with_token = f"https://{WEBHOOK_URL}/{BOT_TOKEN}" # Render автоматически обрабатывает 443 порт

        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT, # Этот PORT - внутренний порт Render для вашего приложения
            url_path=BOT_TOKEN # Path for webhook, usually token
        )
        updater.bot.set_webhook(webhook_url_with_token) # Отдельно устанавливаем webhook
        logger.info(f"Webhook set to {webhook_url_with_token}")
    else:
        # Для локального тестирования можно использовать polling
        logger.info("RENDER_EXTERNAL_HOSTNAME not found, running with polling (for local testing).")
        updater.start_polling() # Изменения здесь!

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle() # Изменения здесь!

if __name__ == "__main__":
    main()
