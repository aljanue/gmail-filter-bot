import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import html
import config
from logger import get_logger
from storage import EmailStorage, ProcessedStorage
from gmail_service import GmailService
from bot_handlers import BotHandlers

logger = get_logger(__name__)


def validate_environment():
    if not config.BOT_TOKEN or config.SECURE_USER_ID == 0:
        logger.critical(
            "Error: TELEGRAM_TOKEN or MY_CHAT_ID missing in the .env file or invalid."
        )
        exit(1)

    if not os.path.exists(config.CREDENTIALS_FILE):
        logger.critical(
            f"MISSING {config.CREDENTIALS_FILE}. Download it from Google Cloud Console."
        )
        exit(1)


async def check_inbox_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    storage: EmailStorage = context.job.data["storage"]
    processed_storage: ProcessedStorage = context.job.data["processed_storage"]
    gmail_service: GmailService = context.job.data["gmail_service"]

    emails_to_monitor = storage.get_all()
    if not emails_to_monitor:
        return

    try:
        messages = gmail_service.fetch_unread_messages(emails_to_monitor)

        for msg in messages:
            if processed_storage.is_processed(msg["id"]):
                continue

            safe_sender = html.escape(msg["sender"])
            safe_subject = html.escape(msg["subject"])
            safe_snippet = html.escape(msg["snippet"])

            await context.bot.send_message(
                chat_id=config.SECURE_USER_ID,
                text=(
                    f"📧 <b>NEW PRIORITY EMAIL</b>\n\n"
                    f"<b>From:</b> {safe_sender}\n"
                    f"<b>Subject:</b> {safe_subject}\n\n"
                    f"<i>{safe_snippet}</i>"
                ),
                parse_mode="HTML",
                disable_notification=False
            )
            logger.info(f"Alert sent for email from {safe_sender}.")

            processed_storage.mark_processed(msg["id"])

    except Exception as e:
        logger.error(f"Exception during Gmail check job: {e}", exc_info=True)


def main():
    logger.info("Initiating production bot startup sequence...")
    validate_environment()

    # Initialize components
    storage = EmailStorage(config.CONFIG_FILE)
    processed_storage = ProcessedStorage(config.PROCESSED_FILE)

    gmail_service = GmailService(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES,
    )

    # Validate Google credentials before starting
    try:
        gmail_service.authenticate()
    except Exception as e:
        logger.critical(f"Critical failure during initial authentication: {e}")
        exit(1)

    handlers = BotHandlers(storage)

    # Initialize Telegram application
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", handlers.cmd_start))
    application.add_handler(CommandHandler("add", handlers.cmd_add))
    application.add_handler(CommandHandler("remove", handlers.cmd_remove))
    application.add_handler(CommandHandler("list", handlers.cmd_list))

    # Schedule the polling daemon
    job_queue = application.job_queue
    job_queue.run_repeating(
        check_inbox_job,
        interval=config.CHECK_INTERVAL,
        first=10,
        data={
            "storage": storage,
            "processed_storage": processed_storage,
            "gmail_service": gmail_service,
        },
    )

    logger.info("🚀 System successfully initialized. Waiting for events...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
