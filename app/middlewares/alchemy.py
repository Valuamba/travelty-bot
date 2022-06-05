import logging
from typing import Any, Awaitable, Callable, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject, User
from aiolimiter import AsyncLimiter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import Config

logger = logging.getLogger(__name__)


class AlchemyMiddleware(BaseMiddleware):
    def __init__(self):
        self.engine = create_async_engine(
            Config.POSTGRESQL_CONNECTION, echo=True,
        )
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        logger.info(f"Connectio to postgresql {Config.POSTGRESQL_CONNECTION}")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.async_session() as session:
            data["alchemy_session"] = session
            await handler(event, data)
