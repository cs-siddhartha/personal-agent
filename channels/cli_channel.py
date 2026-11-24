import asyncio
from channels.base import Channel


class CLIChannel(Channel):
    def __init__(self):
        super().__init__(channel_id="cli")

    async def start(self):
        print("CLI channel ready. Type your messages (Ctrl+C to quit):")
        while True:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\nYou: "
                )
                if not user_input.strip():
                    continue
                if self._message_handler:
                    response = await self._message_handler(
                        self.channel_id, "cli_user", user_input
                    )
                    print(f"\nAgent: {response}")
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

    async def send_message(self, user_id: str, text: str):
        print(f"\nAgent: {text}")