from abc import ABC, abstractmethod
from typing import Callable, Awaitable


class Channel(ABC):
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self._message_handler: Callable[[str, str, str], Awaitable[str]] | None = None

    def set_message_handler(
        self, handler: Callable[[str, str, str], Awaitable[str]]
    ):
        self._message_handler = handler

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def send_message(self, user_id: str, text: str):
        pass