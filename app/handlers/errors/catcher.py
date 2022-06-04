import logging
import os.path

from aiogram import Dispatcher, Bot
from aiogram.types import Update, Message, FSInputFile
from aiogram.utils.markdown import hcode

from app.config import Config
from app.utils.update import get_chat_id, get_chat_id_from_update


async def errors_handler(update: Update, exception, bot: Bot):
    text = "Вызвано необрабатываемое исключение. Администратор был уведомлен об ошибке.\n"
    error = f'Error: {type(exception)}: {exception}'
    document_path = os.path.join(os.getcwd(), "log.log")
    logging.exception(error)
    await bot.send_document(Config.ADMIN_CHAT,
                            document=FSInputFile(path=document_path, filename="log"),
                            caption=f"{hcode(f'Chat id: {get_chat_id_from_update(update)} Error: {type(exception)}: {exception}')}")
    await bot.send_message(chat_id=get_chat_id_from_update(update), text=f"{text}")


def setup(dp: Dispatcher):
    dp.errors.register(errors_handler)
