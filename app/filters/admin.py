from aiogram import types
from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import TelegramObject

from app.config import Config


class AdminFilter(BaseFilter):

    async def __call__(self, obj: TelegramObject, event_chat: types.Chat) -> bool:
        return str(event_chat.id) == Config.ADMIN_CHAT
