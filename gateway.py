from agent import Agent
from channels.base import Channel


class Gateway:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.channels: dict[str, Channel] = {}

    def register_channel(self, channel: Channel):
        channel.set_message_handler(self.handle_message)
        self.channels[channel.channel_id] = channel

    async def handle_message(self, channel_id: str, user_id: str, text: str) -> str:
        session_id = f"{channel_id}:{user_id}"
        response = await self.agent.run_conversation(
            session_id, text, channel_id=channel_id, user_id=user_id
        )
        return response

    async def start(self):
        for channel in self.channels.values():
            await channel.start()
