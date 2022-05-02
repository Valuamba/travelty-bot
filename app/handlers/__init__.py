from aiogram import Dispatcher, Router

from app.handlers import admins, private, errors, test
from app.handlers import updates
from app.handlers.service import service_handlers


def setup_all_handlers(router: Router, admin_router: Router):
    admins.setup(admin_router)
    test.setup(router)
    service_handlers.setup(router)
    # for module in ( private, errors, updates, image_processing):
    # for module in (private, updates):
    #     module.setup(router)
