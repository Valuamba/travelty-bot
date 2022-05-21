from typing import Any

from aiogram import Dispatcher, Bot
from aiogram.dispatcher.filters import BaseFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, TelegramObject

from app.handlers.service.helpers.constants import Fields
from app.models.sql.enums import JuridicalStatus
from app.states.private_states import RoutePrivate
from app.utils.markup_constructor.refactor import refactor_keyboard


class DataValueFilter(BaseFilter):
    key: Any
    value: Any

    # def __init__(self, key, value):
    #     key = key
    #     value = value

    async def __call__(self, obj: TelegramObject, state: FSMContext) -> bool:
        data = await state.get_data()
        return data.get(self.key, None) == self.value


async def get_help_message(m: Message):
    pass


def setup(dp: Dispatcher):
    filters = [DataValueFilter(key=Fields.JURIDICAL_STATUS, value=JuridicalStatus.Individual)]
    dp.message.register(get_help_message, *filters, state=RoutePrivate.PHOTO)
    pass
    # dp.message.register(get_help_message, commands="test")
    # dp.callback_query.register(handle_some,)