import logging
import os
import uuid
from typing import List, Any

import phonenumbers
from aiogram import Dispatcher, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, \
    ContentType
from aiohttp import ClientSession
from geopy import Nominatim

from app.config import Config
from app.handlers.fsm import step_types
from app.handlers.fsm.pipeline import FSMPipeline
from app.handlers.service.helpers.geo import find_place
from app.handlers.service.service_info import \
    juridical_status_info, contact_name_info, company_name_info, service_info, \
    payment_type_info, pick_date_info, select_date_info, commentary_info, photo_info, phone_number_info, \
    accept_result_info, send_route_on_moderation, send_moderated_info
from app.keyboards.private.add_route import AddRouteInlineMarkup, ConfirmTownCD, JuridicalStatusCD, ServiceTypeCD, \
    NavMarkupCD, PaymentCD, PickDateCD
from app.keyboards.simple_calendar import SimpleCalendar, SimpleCalendarCD
from app.models.sql.enums import JuridicalStatus, TripStatus
from app.services.repository import add_new_trip, change_trip_status
from app.states.private_states import RoutePrivate
from app.utils.update import get_chat_id, get_user_id


async def moderate_trip_handler(ctx: CallbackQuery, callback_data: NavMarkupCD, bot: Bot, state: FSMContext, alchemy_session):

    if callback_data.nav_type == "PUBLISH":
        trip = await change_trip_status(callback_data.trip_id, TripStatus.Published, alchemy_session)
        await send_moderated_info(ctx, TripStatus.Published, callback_data.chat_id, callback_data.message_id, trip, bot, state)
    elif callback_data.nav_type == "CANCEL":
        trip = await change_trip_status(callback_data.trip_id, TripStatus.Canceled, alchemy_session)
        await send_moderated_info(ctx, TripStatus.Canceled, callback_data.chat_id, callback_data.message_id, trip, bot, state)
    else:
        raise Exception(f"Wrong nav type: {callback_data.nav_type}")


def setup(dp: Dispatcher):
    dp.callback_query.register(moderate_trip_handler, NavMarkupCD.filter())