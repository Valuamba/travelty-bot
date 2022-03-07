from aiogram import Dispatcher
from aiogram.types import Message, InputFile, FSInputFile
import os
from app.config import Config

async def get_start_message(m: Message):
    await m.answer(
        text='Приветствую!'
                '\n\n📦 Если вам нужно найти попутку, передать документы или посылку, я помогу вам найти нужного человека.'
                '\nДля того, чтобы оставить заявку введите команду: /add_request'
                '\n\n🚚 Если у вас есть возможность передать документы, взять попутчика, передать посылку, введите команду: /add_route \r'
                '\n\n/start - Запуск  бота'
                '\n/help - Помощь'
                '\n/restart - Перезапустить бота и полностью удалить всю информацию бота')


def setup(dp: Dispatcher):
    dp.message.register(get_start_message, commands="start")
