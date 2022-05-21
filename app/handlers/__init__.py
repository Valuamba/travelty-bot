from aiogram import Dispatcher, Router
from app.handlers import admins, private, errors, test
from app.handlers import updates
from app.handlers.service import service_handlers


def setup_all_handlers(router: Router, admin_router: Router):
    admins.setup(admin_router)

    for module in (private, service):
        module.setup(router)
    # for module in (private, updates):
    #     module.setup(router)
