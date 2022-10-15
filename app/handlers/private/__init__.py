from aiogram import Dispatcher

from app.handlers.private import default, start, help_, add_route, test, reply_channel


def setup(dp: Dispatcher):    
    for module in (reply_channel, start, test):
        module.setup(dp)
