from aiogram.types import CallbackQuery, Message


def get_chat_id(update):
    if isinstance(update, CallbackQuery):
        return update.message.chat.id
    elif isinstance(update, Message):
        return update.chat.id
