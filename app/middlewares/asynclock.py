import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject, User

locks = {}

@asynccontextmanager
async def get_lock(id):
    if not locks.get(id):
        locks[id] = asyncio.Lock()
    async with locks[id]:
        yield
    if locks[id]._waiters and len(locks[id]._waiters) == 0:
        del locks[id]


class LockMiddleware(BaseMiddleware):
    def __init__(self):
       pass

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with get_lock(id):
            await handler(event, data)
