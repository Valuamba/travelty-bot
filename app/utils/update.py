from aiogram.types import CallbackQuery, Message, Update


def get_chat_id_from_update(update: Update):
    if update.message:
        return update.message.chat.id
    elif update.callback_query:
        return update.callback_query.message.chat.id


def get_chat_id(update):
    if isinstance(update, CallbackQuery):
        return update.message.chat.id
    elif isinstance(update, Message):
        return update.chat.id

def get_user_id(update):
    if isinstance(update, CallbackQuery):
        return update.from_user.id
    elif isinstance(update, Message):
        return update.from_user.id
