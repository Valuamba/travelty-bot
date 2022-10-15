import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InputFile, FSInputFile, CallbackQuery
from aiogram.dispatcher.fsm.context import FSMContext
import os

from app.config import Config
from app.filters.channel_filter import ChannelReplyFilter
from app.handlers.private.add_route import info_departure_date, info_departure_date_inline
from app.handlers.private.keyboard import MainInlineMarkup, StartMenuCD, StartMenuType
from app.handlers.service.service_handlers import start
from app.utils.update import get_user_id


logger = logging.getLogger(__name__)

async def get_reply_channel(ctx: Message, bot: Bot):
    # -1001715223774
    # if 'Способ оплаты:' in  ctx.text:
        # await bot.send_message(chat_id=ctx.chat.linked_chat_id, reply_to_message_id=ctx.message_id,
        #                        text="Reply")
    await ctx.reply(text=
"""Это объявление было добавлено водителем через бота @travelty_bot, видео с демонстрацией - <a href="https://www.youtube.com/watch?v=r0JG-qRMDVw&ab_channel=Valentin">ссылка</a>.""",
        disable_web_page_preview=True) 
        
    logger.info(f"Reply to message channel {ctx.message_id} in {ctx.chat.id}")
    
   


def setup(dp: Dispatcher):
    dp.message.register(get_reply_channel, ChannelReplyFilter())
