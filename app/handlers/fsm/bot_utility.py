import logging
from contextlib import contextmanager, asynccontextmanager

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)


@asynccontextmanager
async def safe_edit(ctx):
    try:
        yield
    except Exception as exc:
        if isinstance(exc, TelegramBadRequest):
            if "Bad Request: message is not modified:" in exc.message:
                logger.warning("Bad Request: message is not modified:")
                if isinstance(ctx, CallbackQuery):
                    await ctx.answer()
                return
