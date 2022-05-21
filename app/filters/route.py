from aiogram import types
from aiogram.dispatcher.filters import BaseFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import TelegramObject, Message

from app.states.private_states import RoutePrivate


class RouteFilter(BaseFilter):

    async def __call__(self, obj: TelegramObject, state: FSMContext) -> bool:
        if isinstance(obj, Message):
            current_state = await state.get_state()
            return current_state in [state.state for state in RoutePrivate.__all_states__]

