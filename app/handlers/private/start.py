from aiogram import Dispatcher
from aiogram.types import Message, InputFile, FSInputFile
import os
from app.config import Config


async def get_start_message(m: Message):
    await m.answer(
        text='Бот позволяет водителям создавать объявления о их следующей поездке.\n'
             'Все объявления, созданные при помощи бота, публикуются в группе @TraveltyCom.\n\n'
             'Для того, чтобы разместить объявление о вашей поездке, используйте команду - /add_trip\n\n'
             'Обратная связь: @tg_architector')


def setup(dp: Dispatcher):
    dp.message.register(get_start_message, commands="start")
