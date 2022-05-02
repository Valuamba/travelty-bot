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
from app.handlers.service.service_info import departure_town_info, confirm_departure_town_info, arrival_town_info, \
    confirm_arrival_town_info, juridical_status_info, contact_name_info, company_name_info, service_info, \
    payment_type_info, pick_date_info, select_date_info, commentary_info, photo_info, phone_number_info
from app.keyboards.private.add_route import AddRouteInlineMarkup, ConfirmTownCD, JuridicalStatusCD, ServiceTypeCD, \
    NavMarkupCD, PaymentCD, PickDateCD
from app.keyboards.simple_calendar import SimpleCalendar, SimpleCalendarCD
from app.models.sql.enums import JuridicalStatus
from app.states.private_states import RoutePrivate
from app.utils.update import get_chat_id

fsmPipeline = FSMPipeline()
departure_town_pipeline = FSMPipeline()
arrival_town_pipeline = FSMPipeline()
juridical_pipeline = FSMPipeline()
departure_date_pipeline = FSMPipeline()


async def departure_town_handler(msg: Message, bot: Bot, state: FSMContext):
    if len(msg.text) == 0:
        await fsmPipeline.info(msg, bot, state)
    address = get_location(msg.text)
    if len(address) == 0:
        text = f"Не удалось найти город, пожалуйста, повторите ввод."
        await bot.send_message(chat_id=get_chat_id(msg), text=text)
    else:
        await state.update_data(departure_address=address)
        await departure_town_pipeline.next(msg, bot, state)


async def arrival_town_handler(msg: Message, bot: Bot, state: FSMContext):
    if len(msg.text) == 0:
        await fsmPipeline.info(msg, bot, state)

    address = get_location(msg.text)
    if len(address) == 0:
        text = f"Не удалось найти город, пожалуйста, повторите ввод."
        await bot.send_message(chat_id=get_chat_id(msg), text=text)
    else:
        await state.update_data(arrival_address=address)
        await arrival_town_pipeline.next(msg, bot, state)


async def confirm_departure_town_handler(msg: CallbackQuery, callback_data: ConfirmTownCD, bot: Bot, state: FSMContext):
    if callback_data.status == 'yes':
        data = await state.get_data()
        text = "Место отправления: %s" % data['departure_address']['display_name']
        await bot.edit_message_text(chat_id=get_chat_id(msg), message_id=msg.message.message_id, text=text)
        await fsmPipeline.next(msg, bot, state)
    elif callback_data.status == 'no':
        await departure_town_pipeline.prev(msg, bot, state)


async def confirm_arrival_town_handler(msg: CallbackQuery, callback_data: ConfirmTownCD, bot: Bot, state: FSMContext):
    if callback_data.status == 'yes':
        data = await state.get_data()
        text = "Место прибытия: %s" % data['arrival_address']['display_name']
        await bot.edit_message_text(chat_id=get_chat_id(msg), message_id=msg.message.message_id, text=text)
        await fsmPipeline.next(msg, bot, state)
    elif callback_data.status == 'no':
        await arrival_town_pipeline.prev(msg, bot, state)


async def company_name_handler(msg: Message, bot: Bot, state: FSMContext):
    await state.update_data(company_name=msg.text)
    await fsmPipeline.next(msg, bot, state)


async def contact_name_handler(msg: Message, bot: Bot, state: FSMContext):
    await state.update_data(contact_name=msg.text)
    await fsmPipeline.next(msg, bot, state)


async def juridical_status_handler(ctx: CallbackQuery, callback_data: JuridicalStatusCD, bot: Bot, state: FSMContext):
    if callback_data.status == JuridicalStatus.IndividualEntrepreneur:
        await juridical_pipeline.next(ctx, bot, state)
    elif callback_data.status == JuridicalStatus.Individual:
        await state.update_data(juridical_status=callback_data.status)
        await fsmPipeline.next(ctx, bot, state)
    else:
        raise Exception(f'The juridical status [{callback_data.status}] cannot be handled')


async def pick_date_handler(ctx: CallbackQuery, callback_data: PickDateCD, bot: Bot, state: FSMContext):
    await state.update_data(departure_date_id=callback_data.date_id)
    await departure_date_pipeline.next(ctx, bot, state)


async def service_handler(ctx: CallbackQuery, callback_data: ServiceTypeCD, bot: Bot, state: FSMContext):
    services = await add_item_list(state, callback_data.service_type, 'services')
    await state.update_data(services=services)
    await fsmPipeline.info(ctx, bot, state)


async def select_date_handler(ctx: CallbackQuery, callback_data: SimpleCalendarCD, bot: Bot, state: FSMContext):
    await SimpleCalendar().process_selection(ctx, callback_data, bot, state, departure_date_pipeline)


async def payment_type_handler(ctx: CallbackQuery, callback_data: PaymentCD, bot: Bot, state: FSMContext):
    await state.update_data(payment_type=callback_data.payment_type)
    await fsmPipeline.next(ctx, bot, state)


async def commentary_handler(msg: Message, bot: Bot, state: FSMContext):
    if len(msg.text) > 150:
        await bot.send_message(chat_id=get_chat_id(msg),
                               text="Комментарий привышает максимально допустимое кол-во символов 150"
                               )
    else:
        await state.update_data(commentary=msg.text)
        await fsmPipeline.next(msg, bot, state)


async def photo_handler(msg: Message, bot: Bot, state: FSMContext):
    if msg.content_type is ContentType.PHOTO:
        file_id = msg.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        source_directory_path = os.path.join(Config.MEDIA_DIRECTORY_PATH, Config.ROUTE_PHOTO_DIRECTORY)
        if not os.path.exists(source_directory_path):
            os.makedirs(source_directory_path)
        source_path = os.path.join(source_directory_path, uuid.uuid4().__str__() + '.jpg')
        await bot.download_file(file_path, source_path)

        if not os.path.exists(source_path):
            await bot.send_message(msg.chat.id, text='Не получилось скачать фотографию')
        else:
            await state.update_data(photo_path=source_path)
            await fsmPipeline.next(msg, bot, state)
    else:
        await fsmPipeline.info(msg, bot, state)


async def phone_number_handler(msg: Message, bot: Bot, state: FSMContext):
    if msg.content_type is ContentType.TEXT:
        phone_number = phonenumbers.parse(msg.text)
        if phonenumbers.is_valid_number(phone_number):
            await state.update_data(phone_number=msg.text)
            await fsmPipeline.next(msg, bot, state)
        else:
            await bot.send_message(msg.chat.id, text='Не корректный номер телефона, повторите еще раз')
    elif msg.content_type is ContentType.CONTACT:
        await state.update_data(phone_number=msg.contact.phone_number)
        await fsmPipeline.next(msg, bot, state)


async def accept(ctx: Any, bot: Bot, state: FSMContext):
    await fsmPipeline.next(ctx, bot, state)


async def start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await state.update_data(user_id=message.from_user.id)
    await fsmPipeline.move_to(message, bot, state, fsmPipeline.pipeline[0].state)


def get_location(query: str):
    address = {}
    geolocator = Nominatim(user_agent="travelty-bot")
    locations = geolocator.geocode(
        query=query,
        timeout=10, exactly_one=False, language='ru', namedetails=True, addressdetails=True
    )

    if locations and len(locations) > 0:
        locations = sorted(locations,
                           key=lambda l: (l.raw is not None and 'address' in l.raw and 'country' in l.raw['address']),
                           reverse=True
                           )
        location = locations[0]
        if location.raw:
            if 'address' in location.raw:
                address = location.raw['address']
                address['place_id'] = location.raw['place_id']
                address['osm_id'] = location.raw['osm_id']
                address['display_name'] = location.raw['display_name']

    return address


async def add_item_list(state, item, key) -> List[Any]:
    data = await state.get_data()
    array = data.get(key, [])
    if item in array:
        array.remove(item)
    else:
        array.append(item)
    return array


def setup(dp: Dispatcher):
    dp.message.register(start, commands="find")
    accept_rule = (NavMarkupCD.filter(), accept)

    departure_town_pipeline.set_pipeline([
        step_types.MessageStep(state=RoutePrivate.DEPARTURE_TOWN, handler=departure_town_handler,
                               info_handler=departure_town_info
                               ),
        step_types.CallbackStep(state=RoutePrivate.CONFIRM_DEPARTURE_TOWN, handler=confirm_departure_town_handler,
                                info_handler=confirm_departure_town_info,
                                filter=ConfirmTownCD.filter()
                                )
    ]
    )
    departure_town_pipeline.build(dp)

    arrival_town_pipeline.set_pipeline([
        step_types.MessageStep(state=RoutePrivate.ARRIVAL_TOWN, handler=arrival_town_handler,
                               info_handler=arrival_town_info
                               ),
        step_types.CallbackStep(state=RoutePrivate.CONFIRM_ARRIVAL_TOWN, handler=confirm_arrival_town_handler,
                                info_handler=confirm_arrival_town_info,
                                filter=ConfirmTownCD.filter()
                                )
    ]
    )
    arrival_town_pipeline.build(dp)

    juridical_pipeline.set_pipeline([
        step_types.CallbackStep(state=RoutePrivate.JURIDICAL_STATUS, handler=juridical_status_handler,
                                info_handler=juridical_status_info,
                                filter=JuridicalStatusCD.filter()
                                ),
        step_types.MessageStep(state=RoutePrivate.COMPANY_NAME, handler=company_name_handler,
                               info_handler=company_name_info
                               ),
    ]
    )

    departure_date_pipeline.set_pipeline([
        step_types.CallbackStep(state=RoutePrivate.PICK_DATE_ID, handler=pick_date_handler,
                                info_handler=pick_date_info,
                                filter=PickDateCD.filter(),
                                inline_navigation_handler=[accept_rule]
                                ),
        step_types.CallbackStep(state=RoutePrivate.SELECT_DATE, handler=select_date_handler,
                                info_handler=select_date_info,
                                filter=SimpleCalendarCD.filter(),
                                ),
    ]
    )

    commentary = step_types.MessageStep(state=RoutePrivate.COMMENTARY, handler=commentary_handler,
                                        info_handler=commentary_info
                                        )

    payment_type = step_types.CallbackStep(state=RoutePrivate.PAYMENT_TYPE, handler=payment_type_handler,
                                           info_handler=payment_type_info, filter=PaymentCD.filter()
                                           )

    service_type = step_types.CallbackStep(state=RoutePrivate.SELECT_SERVICE, handler=service_handler,
                                           info_handler=service_info,
                                           filter=ServiceTypeCD.filter(),
                                           inline_navigation_handler=[accept_rule]
                                           )

    contact_name = step_types.MessageStep(state=RoutePrivate.CONTACT_NAME, handler=contact_name_handler,
                                          info_handler=contact_name_info
                                          )
    photo = step_types.MessageStep(state=RoutePrivate.PHOTO, handler=photo_handler,
                                          info_handler=photo_info
                                          )

    phone_number = step_types.MessageStep(state=RoutePrivate.PHOTO_NUMBER, handler=phone_number_handler,
                                          info_handler=phone_number_info
                                          )

    fsmPipeline.set_pipeline([
        phone_number,
        photo,
        commentary,
        payment_type,
        departure_date_pipeline,
        service_type,
        juridical_pipeline,
        contact_name,
        departure_town_pipeline,
        arrival_town_pipeline
    ]
    )
    fsmPipeline.build(dp)
