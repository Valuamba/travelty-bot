from aiogram import Dispatcher
from aiogram.utils.i18n import I18nMiddleware

from .acl import ACLMiddleware
from .alchemy import AlchemyMiddleware
from .asynclock import LockMiddleware
from .clocks import ClocksMiddleware
from .throttling import ThrottlingMiddleware
import os

I18N_DOMAIN = 'mybot'

LOCALES_DIR = os.path.join(os.getcwd(), 'localization/')


def setup(dp: Dispatcher):
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(ClocksMiddleware())
    dp.callback_query.middleware(ClocksMiddleware())
    dp.update.outer_middleware(ACLMiddleware())
    dp.update.outer_middleware(LockMiddleware())
    dp.update.outer_middleware(AlchemyMiddleware())
