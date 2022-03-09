from aiogram import Dispatcher

from app.handlers.private import default, start, help_, add_route


def setup(dp: Dispatcher):
    for module in (start, add_route):
        module.setup(dp)
