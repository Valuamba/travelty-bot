from aiogram import Dispatcher

from app.handlers.service import service_handlers


def setup(dp: Dispatcher):

    for module in (service_handlers, ):
        module.setup(dp)
