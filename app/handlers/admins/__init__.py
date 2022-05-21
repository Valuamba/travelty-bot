from aiogram import Router, Dispatcher

from app.filters.admin import AdminFilter
from app.handlers.admins import broadcast, commands, moderate_trip


def setup(router: Dispatcher):
    router.message.filter(AdminFilter())
    router.callback_query.filter(AdminFilter())

    for module in (moderate_trip, ):
        module.setup(router)
