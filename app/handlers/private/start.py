from aiogram import Dispatcher
from aiogram.types import Message, InputFile, FSInputFile
import os
from app.config import Config


async def get_start_message(m: Message):
    text = []
    text.append('👋 <b>Приветствую!</b>\n')
    text.append('Я, <b>Трэвэлти</b> 🤖, помогаю водителям и перевозчикам найти людей заинтересованных в <b>трансфере</b>, <b>передаче посылок</b> или <b>документов</b>.\n')
    text.append('<b>Как это работает:</b>')
    text.append('  - ✒️водитель заполняет объявление через бота;')
    text.append('  - ✅ объявление проходит модерацию;')
    text.append('  - 🔐 объявление публикуется в группе @TraveltyCom;\n')
    text.append('🛣 Объявление содержит полный маршрут с <b>датами отправления</b>, <b>контактами водителя</b> и ссылкой на <b>Яндекс Карты</b>.\n')
    text.append('👁‍️Водитель может <u>копировать текст объявления</u>, <u>присылать ссылку</u> на объявление своим клиентам.\n')
    text.append('💫 Для того, чтобы разместить объявление о вашей поездке, используйте команду - /add_trip <i>(нажмите)</i>.\n')
    text.append('<b>Обратная связь:</b> @tg_architector.')

    await m.answer(text='\n'.join(text))


def setup(dp: Dispatcher):
    dp.message.register(get_start_message, commands="start")
