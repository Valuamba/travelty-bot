from aiogram import Dispatcher

from app.handlers.private import default, start, help_


def setup(dp: Dispatcher):
    for module in (start, ):
        module.setup(dp)
