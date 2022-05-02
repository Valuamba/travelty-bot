from aiogram import Dispatcher, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.markup_constructor.refactor import refactor_keyboard


async def get_help_message(m: Message):
    refactor_keyboard(2, 8)
    some_inl = InlineKeyboardButton(text='some', callback_data='some')
    extra_some_inl = InlineKeyboardButton(text='some some some', callback_data='some')
    kok_inl = InlineKeyboardButton(text='Перевоз крупногабаритных предметов', callback_data='some')
    await m.answer("This is a bot",
                   reply_markup=InlineKeyboardMarkup(
                       inline_keyboard = [
                           [some_inl, some_inl],
                           [some_inl, some_inl],
                           [extra_some_inl, some_inl],
                           [kok_inl, some_inl],
                           [some_inl, some_inl],
                       ]
                   ))
    # await m.answer("This is a bot", reply_markup=GetServiceMarkup().get())
    # await m.answer("This is a bot", reply_markup=NavMarkup().get())


async def handle_some(ctx: CallbackQuery, bot: Bot):
    pass


def setup(dp: Dispatcher):
    pass
    # dp.message.register(get_help_message, commands="test")
    # dp.callback_query.register(handle_some,)