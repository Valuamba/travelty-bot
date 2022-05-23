import datetime
import os
from enum import Enum
from typing import Any, List, Optional
from aiogram import Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from app.handlers.fsm.step_types import UTILITY_MESSAGE_IDS, MAIN_STEP_MESSAGE_ID
from app.utils.update import get_chat_id


class StepInfoType(Enum):
    Main = 1,
    Utility = 2


async def add_item_list(state, item, key) -> List[Any]:
    data = await state.get_data()
    array = data.get(key, [])
    if item in array:
        array.remove(item)
    else:
        array.append(item)
    return array


async def step_info(ctx: Any, state: FSMContext, bot: Bot, text, reply_markup=None, step_info_type=StepInfoType.Main,
                    update_type: Any = None, disable_notification: Optional[bool]=None):
    data = await state.get_data()
    main_step_message = data.get(MAIN_STEP_MESSAGE_ID, None)

    async def main_message():
        message = await bot.send_message(chat_id=get_chat_id(ctx), text=text, parse_mode='HTML',
                                         reply_markup=reply_markup, disable_notification=disable_notification
                                         )
        data[MAIN_STEP_MESSAGE_ID] = message.message_id
        await state.update_data(data)

    async def utility_message():
        message = await bot.send_message(chat_id=get_chat_id(ctx), text=text, parse_mode='HTML',
                                         reply_markup=reply_markup, disable_notification=disable_notification
                                         )
        utility_ids = await add_item_list(state, message.message_id, UTILITY_MESSAGE_IDS)
        await state.update_data(**{UTILITY_MESSAGE_IDS: utility_ids})

    async def message_switch():
        if step_info_type == StepInfoType.Main:
            await main_message()
        elif step_info_type == StepInfoType.Utility:
            await utility_message()
        else:
            raise Exception(f'Step info type {step_info_type} doesent supported')

    async def callback_switch():
        if step_info_type == StepInfoType.Main:
            await bot.edit_message_text(chat_id=get_chat_id(ctx), message_id=main_step_message, parse_mode='HTML', text=text,
                                        reply_markup=reply_markup)
        elif step_info_type == StepInfoType.Utility:
            await bot.edit_message_text(chat_id=get_chat_id(ctx), message_id=ctx.message.message_id,
                                        parse_mode='HTML', text=text,
                                        reply_markup=reply_markup
                                        )

    if update_type == Message:
        await message_switch()
    elif main_step_message and update_type == CallbackQuery:
        await callback_switch()
    elif isinstance(ctx, Message):
        await message_switch()
    elif main_step_message and isinstance(ctx, CallbackQuery):
        await callback_switch()
    elif not main_step_message:
        await message_switch()
    else:
        raise Exception(f'Step info type {step_info_type} doesent supported')