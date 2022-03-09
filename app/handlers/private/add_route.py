from typing import cast, AsyncGenerator, Union
from aiogram import types, Router, Bot, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery

from app.filters.private import ServiceTypeFilter
from app.keyboards.admin.inline import CancelKb
from app.keyboards.private.inline import ConfirmTownMarkup, GetPaymentMarkup, GetServiceMarkup
from app.keyboards.private.reply import RouteReplyMarkup
from app.models import UserModel
from app.models.route import PaymentTypeLocales
from app.states.admin_states import BroadcastAdmin
from app.states.private_states import RoutePrivate
from app.utils.broadcast import broadcast_smth
from geopy.geocoders import Nominatim
import pprint
import json

from app.utils.update import get_chat_id

geolocator = Nominatim(user_agent="travelty-bot")


async def info_departure_date(msg: Message, state: FSMContext):
    await state.set_state(RoutePrivate.departure_date)
    await msg.answer('Введите дату, когда вы будете ехать в формате ДД.ММ.ГГГГ (например, 22.03.2022):',
                     reply_markup=RouteReplyMarkup().get_back_markup())


async def info_departure_town(ctx: Union[CallbackQuery, Message], state: FSMContext, bot: Bot):
    await state.set_state(RoutePrivate.departure_town)
    await bot.send_message(get_chat_id(ctx), text=f'Введите город отправления (например, Брест):',
                           reply_markup=RouteReplyMarkup().get_back_markup())


async def info_arrival_town(ctx: Union[CallbackQuery, Message], state: FSMContext, bot: Bot):
    await state.set_state(RoutePrivate.arrival_town)
    await bot.send_message(get_chat_id(ctx), text='Введите город прибытия (например, Брест):',
                           reply_markup=RouteReplyMarkup().get_back_markup())


async def info_confirm_departure_town(ctx: Union[CallbackQuery, Message], state: FSMContext):
    await state.set_state(RoutePrivate.confirm_departure_town)
    data = await state.get_data()
    full_address = data['departure_displayed_address']
    await ctx.answer(text=f'Введенный вами адрес: {full_address}',
                     reply_markup=ConfirmTownMarkup().get())


async def info_confirm_arrival_town(ctx: Union[CallbackQuery, Message], state: FSMContext):
    await state.set_state(RoutePrivate.confirm_arrival_town)
    data = await state.get_data()
    full_address = data['arrival_displayed_address']
    await ctx.answer(text=f'Введенный вами адрес: {full_address}',
                     reply_markup=ConfirmTownMarkup().get())


async def info_complete(ctx: Union[CallbackQuery, Message], state: FSMContext, bot: Bot):
    await state.set_state(RoutePrivate.complete)
    await bot.send_message(get_chat_id(ctx), text="Маршрут был добален успешно")


async def info_payment_type(ctx: Union[CallbackQuery, Message], state: FSMContext, bot: Bot):
    await state.set_state(RoutePrivate.choose_payment_type)
    await bot.send_message(get_chat_id(ctx), text='Выберите тип вознаграждения:',
                           reply_markup=GetPaymentMarkup().get())


async def info_service_type(ctx: Union[CallbackQuery, Message], state: FSMContext, bot: Bot):
    await state.set_state(RoutePrivate.select_service)
    await bot.send_message(get_chat_id(ctx), text='Выберите услуги, которые вы будете готовы оказать:',
                           reply_markup=GetServiceMarkup().get())


async def service_type(ctx: CallbackQuery, callback_data: GetServiceMarkup.CD, state: FSMContext, bot: Bot):
    data = await state.get_data()
    services = data.get('services', [])
    if callback_data.service_type in services:
        services.remove(callback_data.service_type)
    else:
        services.append(callback_data.service_type)
    await state.update_data(services=services)
    await bot.edit_message_reply_markup(get_chat_id(ctx), ctx.message.message_id,
                                        reply_markup=GetServiceMarkup().get(services))


async def add_route_command(msg: Message, state: FSMContext):
    await info_departure_date(msg, state)


async def departure_date(msg: Message, state: FSMContext, bot: Bot):
    await state.update_data(departure_date=msg.text)
    await info_departure_town(msg, state, bot)


async def departure_town(msg: Message, state: FSMContext, bot: Bot):
    location = geolocator.geocode(query=msg.text, timeout=10, language='ru', namedetails=True, addressdetails=True)
    if location is None:
        await msg.answer(text="Не удалось найти на карте введенный вами адрес. Попробуйте еще раз.")
        await info_departure_town(msg, state, bot)
    else:
        await state.update_data(departure_town_address=location.raw['address'])
        await state.update_data(departure_displayed_address=location.raw['display_name'])
        await info_confirm_departure_town(msg, state)


async def arrival_town(msg: Message, state: FSMContext, bot: Bot):
    location = geolocator.geocode(query=msg.text, timeout=10, language='ru', namedetails=True, addressdetails=True)
    if location is None:
        await msg.answer(text="Не удалось найти на карте введенный вами адрес. Попробуйте еще раз.")
        await info_arrival_town(msg, state, bot)
    else:
        await state.update_data(arrival_town_address=location.raw['address'])
        await state.update_data(arrival_displayed_address=location.raw['display_name'])
        await info_confirm_arrival_town(msg, state)


async def payment_type(ctx: CallbackQuery, callback_data: GetPaymentMarkup.CD, state: FSMContext, bot: Bot):
    await state.update_data(payment_type=callback_data.payment_type)
    await bot.edit_message_text(f'Выбранный тип: {PaymentTypeLocales[callback_data.payment_type]}',
                                ctx.message.chat.id, ctx.message.message_id)
    await info_service_type(ctx, state, bot)


async def confirm_departure_town(ctx: CallbackQuery, callback_data: ConfirmTownMarkup.CD, state: FSMContext, bot: Bot):
    if callback_data.status == 'yes':
        await info_arrival_town(ctx, state, bot)
    elif callback_data.status == 'no':
        await info_departure_town(ctx, state, bot)


async def confirm_arrival_town(ctx: CallbackQuery, callback_data: ConfirmTownMarkup.CD, state: FSMContext, bot: Bot):
    if callback_data.status == 'yes':
        await info_payment_type(ctx, state, bot)
    elif callback_data.status == 'no':
        await info_arrival_town(ctx, state, bot)


async def cancel(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == RoutePrivate.departure_town.state:
        await info_departure_date(msg, state)
    elif current_state == RoutePrivate.arrival_town.state:
        await info_departure_town(msg, state)


def setup(router: Router):
    router.message.register(add_route_command, commands="add_route")
    router.message.register(cancel, text='Назад', state="*", content_types=types.ContentType.TEXT)
    router.callback_query.register(confirm_departure_town, ConfirmTownMarkup.CD.filter(), state=RoutePrivate.confirm_departure_town)
    router.callback_query.register(confirm_arrival_town, ConfirmTownMarkup.CD.filter(), state=RoutePrivate.confirm_arrival_town)
    router.callback_query.register(payment_type, GetPaymentMarkup.CD.filter(), state=RoutePrivate.choose_payment_type)
    router.callback_query.register(service_type, GetServiceMarkup.CD.filter(ServiceTypeFilter), state=RoutePrivate.select_service)
    router.message.register(departure_date, state=RoutePrivate.departure_date, content_types=types.ContentType.TEXT)
    router.message.register(departure_town, state=RoutePrivate.departure_town, content_types=types.ContentType.TEXT)
    router.message.register(arrival_town, state=RoutePrivate.arrival_town, content_types=types.ContentType.TEXT)
