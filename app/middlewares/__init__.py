from aiogram import Dispatcher
from aiogram.utils.i18n import I18nMiddleware

from .acl import ACLMiddleware
from .clocks import ClocksMiddleware
from .throttling import ThrottlingMiddleware
import os

I18N_DOMAIN = 'mybot'

LOCALES_DIR = os.path.join(os.getcwd(), 'localization/')

def setup(dp: Dispatcher):
    dp.message.middleware(ThrottlingMiddleware())
    # dp.callback_query.middlewares(ThrottlingMiddleware())
    dp.message.middleware(ClocksMiddleware())
    dp.callback_query.middleware(ClocksMiddleware())
    dp.update.outer_middleware(ACLMiddleware())
