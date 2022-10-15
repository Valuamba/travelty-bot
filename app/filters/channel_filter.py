from aiogram import types
from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import TelegramObject, Message

from app.config import Config


class ChannelReplyFilter(BaseFilter):

    async def __call__(self, obj: TelegramObject, event_chat: types.Chat) -> bool:
        if isinstance(obj, Message):
            return str(event_chat.id) == Config.DISCUSSION_CHANNEL and 'Способ оплаты:' in  obj.caption
        
        return False

