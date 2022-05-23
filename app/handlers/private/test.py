import os

from aiogram import Dispatcher, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from magic_filter import F

from app.config import Config
from app.filters.private import ServiceTypeFilter
from app.utils.route_mapping import map_route_data_to_str


async def get_help_message(m: Message, bot):
    file_path = os.path.join(os.getcwd(), 'assets/no_photo.jpg')
    await bot.send_photo(chat_id=m.chat.id,
                         photo=FSInputFile(path=file_path, filename="img"),
                         caption=map_route_data_to_str()
                         )
    # await m.answer(text=map_route_data_to_str(), disable_web_page_preview=True)
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
    # dp.callback_query.register(handle_some,)
