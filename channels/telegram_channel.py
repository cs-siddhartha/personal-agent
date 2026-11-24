import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from channels.base import Channel


class TelegramChannel(Channel):
    def __init__(self):
        super().__init__(channel_id="telegram")
        self.app: Application | None = None

    async def start(self):
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token:
            print("Warning: TELEGRAM_BOT_TOKEN not set. Telegram channel disabled.")
            return

        self.app = Application.builder().token(token).build()

        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        print("Telegram channel connected.")

    async def _handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await update.message.reply_text(
            "Hello! I am your personal AI agent. Send me a message!"
        )

    async def _handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not update.message or not update.message.text:
            return
        user_id = str(update.effective_user.id)
        text = update.message.text

        if self._message_handler:
            response = await self._message_handler(self.channel_id, user_id, text)
            await update.message.reply_text(response)

    async def send_message(self, user_id: str, text: str):
        if self.app:
            await self.app.bot.send_message(chat_id=int(user_id), text=text)

    async def stop(self):
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()