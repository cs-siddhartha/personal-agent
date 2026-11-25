import os

from telegram import Update
from telegram.constants import ChatType
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
        self._owner_id: int | None = None

    async def start(self):
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token:
            print("Warning: TELEGRAM_BOT_TOKEN not set. Telegram channel disabled.")
            return

        owner_id = os.environ.get("TELEGRAM_OWNER_ID", "").strip()
        if not owner_id.isdecimal() or int(owner_id) <= 0:
            print(
                "Warning: TELEGRAM_OWNER_ID must be a positive user ID. Telegram channel disabled."
            )
            return
        self._owner_id = int(owner_id)

        self.app = Application.builder().token(token).build()

        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        print("Telegram channel connected.")

    # Both interactive handlers require the configured owner's private chat.
    def _is_owner_chat(self, update: Update) -> bool:
        chat = update.effective_chat
        user = update.effective_user
        return (
            chat is not None
            and chat.type == ChatType.PRIVATE
            and chat.id == self._owner_id
            and user is not None
            and user.id == self._owner_id
        )

    async def _handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if update.message and self._is_owner_chat(update):
            await update.message.reply_text(
                "Hello! I am your personal AI agent. Send me a message!"
            )

    async def _handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if (
            not update.message
            or not update.message.text
            or not self._is_owner_chat(update)
        ):
            return
        user_id = str(update.effective_user.id)
        text = update.message.text

        if self._message_handler:
            response = await self._message_handler(self.channel_id, user_id, text)
            await update.message.reply_text(response)

    async def send_message(self, user_id: str, text: str):
        owner_id = self._owner_id
        if self.app and owner_id is not None and user_id == str(owner_id):
            await self.app.bot.send_message(chat_id=owner_id, text=text)

    async def stop(self):
        if self.app:
            if self.app.updater and self.app.updater.running:
                await self.app.updater.stop()
            if self.app.running:
                await self.app.stop()
            await self.app.shutdown()
