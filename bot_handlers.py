from telegram import Update
from telegram.ext import ContextTypes
from config import SECURE_USER_ID
from logger import get_logger
from storage import EmailStorage

logger = get_logger(__name__)

class BotHandlers:
    def __init__(self, storage: EmailStorage):
        self.storage = storage

    async def is_authorized_user(self, update: Update) -> bool:
        if not update.effective_user or update.effective_user.id != SECURE_USER_ID:
            logger.warning(f"Access denied attempt from user ID: {update.effective_user.id if update.effective_user else 'Unknown'}")
            return False
        return True

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.is_authorized_user(update): return
        await update.message.reply_text(
            "✅ Secure Gmail Monitoring System Online.\n"
            "Commands available: /add, /remove, or /list."
        )

    async def cmd_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.is_authorized_user(update): return
        if not context.args:
            await update.message.reply_text("⚠️ Correct usage: /add email@domain.com")
            return
            
        email = context.args[0].lower().strip()
        added = self.storage.add(email)
        
        if added:
            logger.info(f"New sender added: {email}")
            await update.message.reply_text(f"🔔 Monitoring activated for: {email}")
        else:
            await update.message.reply_text("ℹ️ That sender is already being monitored.")

    async def cmd_remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.is_authorized_user(update): return
        if not context.args: return
        
        email = context.args[0].lower().strip()
        removed = self.storage.remove(email)
        
        if removed:
            logger.info(f"Sender removed: {email}")
            await update.message.reply_text(f"🗑️ Monitoring deactivated for: {email}")
        else:
            await update.message.reply_text("ℹ️ That sender is not being monitored.")

    async def cmd_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.is_authorized_user(update):
            return
        
        emails = self.storage.get_all()
        if not emails:
            await update.message.reply_text("📋 The monitoring list is empty.")
            return
            
        email_list = "\n".join(f"- {email}" for email in emails)
        await update.message.reply_text(f"📋 <b>Monitored senders:</b>\n{email_list}", parse_mode='HTML')
