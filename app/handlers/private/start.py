import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InputFile, FSInputFile, CallbackQuery
from aiogram.dispatcher.fsm.context import FSMContext
import os

from app.config import Config
from app.handlers.private.add_route import info_departure_date, info_departure_date_inline
from app.handlers.private.keyboard import MainInlineMarkup, StartMenuCD, StartMenuType
from app.handlers.service.service_handlers import start
from app.utils.update import get_user_id


logger = logging.getLogger(__name__)

async def get_start_message(ctx: Message, bot: Bot):
    
    text = []
    text.append('👋 <b>Приветствую!</b>\n')
    text.append('Я, <b>Трэвэлти</b> 🤖, помогаю водителям найти пассажиров.\n')
    text.append('<b>Как это работает:</b>')
    text.append('  - водитель заполняет объявление через бота;')
    text.append('  - объявление проходит модерацию 5-15 мин, 08:00-23:00 МСК;')
    text.append('  - объявление публикуется в группе @TraveltyCom;\n')
    text.append('<b>Служба поддержки:</b> @travelty_staff (08:00-23:00 МСК).')

    # path = os.path.join(Config.ROOT_DIR, 'app/assets/TRAVELTY_bot.png')
    path = os.path.join(Config.ROOT_DIR, 'app/assets/1.png')
    logo = FSInputFile(path, "logo")

    logger.info(f"Start command with logo {path}")

    await bot.send_photo(chat_id=get_user_id(ctx), 
                         photo=logo,
                         caption='\n'.join(text), reply_markup=MainInlineMarkup().get_start_command_keyboard())
    # await m.answer(text='\n'.join(text), reply_markup=MainInlineMarkup().get_start_command_keyboard())


async def handle_start_menu(ctx: CallbackQuery, callback_data: StartMenuCD, bot: Bot, state: FSMContext):
    if callback_data.type == StartMenuType.CREATE_ROUTE:
        await start(ctx, bot, state)
        

def setup(dp: Dispatcher):
    dp.message.register(get_start_message, commands="start")
    dp.callback_query.register(handle_start_menu, StartMenuCD.filter())
