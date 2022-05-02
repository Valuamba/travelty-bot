from aiogram import Dispatcher, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from magic_filter import F

from app.filters.private import ServiceTypeFilter

async def get_help_message(m: Message):
    pass
    # await m.answer("This is a bot",
    #                reply_markup=InlineKeyboardMarkup(
    #                    inline_keyboard = [
    #                        [InlineKeyboardButton(text='some', callback_data='some')]
    #                    ]
    #                ))
    # await m.answer("This is a bot", reply_markup=GetServiceMarkup().get())
    # await m.answer("This is a bot", reply_markup=NavMarkup().get())


async def handle_some(ctx: CallbackQuery, bot: Bot):
    pass


def setup(dp: Dispatcher):
    dp.message.register(get_help_message, commands="test")
    dp.callback_query.register(handle_some,)
