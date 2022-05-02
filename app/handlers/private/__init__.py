from aiogram import Dispatcher

from app.handlers.private import default, start, help_, add_route, test


def setup(dp: Dispatcher):
    pass
    # for module in (start, ):
    # # for module in (test, ):
    #     module.setup(dp)
