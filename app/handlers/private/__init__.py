from aiogram import Dispatcher

from app.handlers.private import default, start, help_, add_route, test


def setup(dp: Dispatcher):
    for module in (start, test):
        module.setup(dp)
