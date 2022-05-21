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
from app.handlers.service.service_info import departure_town_info, confirm_departure_town_info, arrival_town_info, \
    confirm_arrival_town_info, juridical_status_info, contact_name_info, company_name_info, service_info, \
    payment_type_info, pick_date_info, select_date_info, commentary_info, photo_info, phone_number_info, \
    accept_result_info
from app.keyboards.private.add_route import AddRouteInlineMarkup, ConfirmTownCD, JuridicalStatusCD, ServiceTypeCD, \
    NavMarkupCD, PaymentCD, PickDateCD
from app.keyboards.simple_calendar import SimpleCalendar, SimpleCalendarCD
from app.models.sql.enums import JuridicalStatus
from app.states.private_states import RoutePrivate
from app.utils.update import get_chat_id, get_user_id

route_pipeline = FSMPipeline()

