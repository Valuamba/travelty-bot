import asyncio
import logging
import os
import uuid
from typing import List, Any, Optional

import aiogram
import phonenumbers
from CommandNotFound.db.creator import measure
from aiogram import Dispatcher, Bot, F, MagicFilter
from aiogram.dispatcher.event.handler import FilterType
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, \
    ContentType
from aiohttp import ClientSession
from geopy import Nominatim

from app.config import Config
from app.filters.route import RouteFilter
from app.handlers.fsm import step_types
from app.handlers.fsm.fsm_utility import step_info, StepInfoType
from app.handlers.fsm.pipeline import FSMPipeline
from app.handlers.fsm.step_types import UTILITY_MESSAGE_IDS
from app.handlers.service.helpers.constants import Fields, MapRouteStateToField
from app.handlers.service.helpers.geo import find_place
from app.handlers.service.service_info import \
    juridical_status_info, contact_name_info, company_name_info, service_info, \
    payment_type_info, pick_date_info, select_date_info, commentary_info, photo_info, phone_number_info, \
    accept_result_info, send_route_on_moderation, pick_route_point, address_info, confirm_address_info, form_info
from app.handlers.test import DataValueFilter
from app.keyboards.private.add_route import AddRouteInlineMarkup, ConfirmTownCD, JuridicalStatusCD, ServiceTypeCD, \
    NavMarkupCD, PaymentCD, PickDateCD, PickAddressCD, FormCD
from app.keyboards.simple_calendar import SimpleCalendar, SimpleCalendarCD
from app.models.sql.enums import JuridicalStatus
from app.services.repository import add_new_trip
from app.states.private_states import RoutePrivate
from app.utils.logger import log_handler
from app.utils.update import get_chat_id, get_user_id

fsmPipeline = FSMPipeline()
address_pipeline = FSMPipeline()
departure_date_pipeline = FSMPipeline()


async def pick_route_handler(ctx: CallbackQuery, callback_data: PickAddressCD, bot: Bot, state: FSMContext):
    await state.update_data(address_key=callback_data.address_key)
    await address_pipeline.next(ctx, bot, state)


async def address_handler(msg: Message, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("address_handler", get_user_id(msg), current_state)

    data = await add_utility_message(msg, state, True)

    if len(msg.text) == 0:
        await fsmPipeline.info(msg, bot, state)

    address = find_place(msg.text)
    if address:
        data['current_address'] = address
        await state.update_data(data)
        await address_pipeline.next(msg, bot, state)
    else:
        await step_info(msg, state, bot, text="Не удалось найти город, пожалуйста, повторите ввод.",
                        step_info_type=StepInfoType.Utility
                        )


async def address_confirm_handler(msg: CallbackQuery, callback_data: ConfirmTownCD, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("address_confirm_handler", get_user_id(msg), current_state)

    if callback_data.status == 'yes':
        data = await state.get_data()
        # if await _valid_address(msg, bot, state, data, data['current_address']):
        address_key = data['address_key']
        data[address_key] = data['current_address']
        await state.update_data(data)
        await address_pipeline.clean(msg, bot, state)
        await address_pipeline.move_to(msg, bot, state, RoutePrivate.PICK_ADDRESS)
        # else:
        #     await address_pipeline.prev(msg, bot, state, only_state=True)
        #     await state.update_data(data)
    elif callback_data.status == 'no':
        await address_pipeline.clean(msg, bot, state)
        await address_pipeline.prev(msg, bot, state, only_state=True)


async def _valid_address(ctx: CallbackQuery, bot: Bot, state: FSMContext, data: dict, value):
    for key in data['address_points']:
        address = data.get(key, None)
        if address and value['place_id'] == address['place_id']:
            data['current_address'] = None
            await step_info(ctx, state, bot, text="❗️Введенный вами адрес уже добавлен в маршрут.\n Введите новый адрес.",
                            step_info_type=StepInfoType.Utility
                            )
            return False

    return True


async def company_name_handler(msg: Message, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("company_name_handler", get_user_id(msg), current_state)

    data = await add_utility_message(msg, state)
    data[Fields.COMPANY_NAME] = msg.text
    await state.update_data(data)
    await next(msg, bot, state)


async def contact_name_handler(msg: Message, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("contact_name_handler", get_user_id(msg), current_state)

    data = await add_utility_message(msg, state)
    data[Fields.CONTACT_NAME] = msg.text
    await state.update_data(data)
    await next(msg, bot, state)


async def juridical_status_handler(ctx: CallbackQuery, callback_data: JuridicalStatusCD, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("juridical_status_handler", get_user_id(ctx), current_state)

    if callback_data.status == JuridicalStatus.IndividualEntrepreneur:
        await state.update_data(**{Fields.JURIDICAL_STATUS: callback_data.status})
        await fsmPipeline.next(ctx, bot, state)
    elif callback_data.status == JuridicalStatus.Individual:
        await state.update_data(**{Fields.JURIDICAL_STATUS: callback_data.status})
        await fsmPipeline.next(ctx, bot, state)
    else:
        raise Exception(f'The juridical status [{callback_data.status}] cannot be handled')


async def pick_date_handler(ctx: CallbackQuery, callback_data: PickDateCD, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("pick_date_handler", get_user_id(ctx), current_state)

    await state.update_data(departure_date_id=callback_data.date_id)
    await departure_date_pipeline.next(ctx, bot, state)


async def service_handler(ctx: CallbackQuery, callback_data: ServiceTypeCD, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("service_handler", get_user_id(ctx), current_state)

    services = await add_item_list(state, callback_data.service_type, 'services')
    await state.update_data(**{Fields.SERVICES: services})
    await fsmPipeline.info(ctx, bot, state)


async def select_date_handler(ctx: CallbackQuery, callback_data: SimpleCalendarCD, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("select_date_handler", get_user_id(ctx), current_state)

    await SimpleCalendar().process_selection(ctx, callback_data, bot, state, departure_date_pipeline)


async def payment_type_handler(ctx: CallbackQuery, callback_data: PaymentCD, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("payment_type_handler", get_user_id(ctx), current_state)

    await state.update_data(**{Fields.PAYMENT_TYPE: callback_data.payment_type})
    await next(ctx, bot, state)


async def commentary_handler(msg: Message, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("commentary_handler", get_user_id(msg), current_state)

    data = await add_utility_message(msg, state, True)

    if len(msg.text) > 150:
        await step_info(msg, state, bot, text="Комментарий привышает максимально допустимое кол-во символов 150",
                        step_info_type=StepInfoType.Utility)
    else:
        data[Fields.COMMENTARY]=msg.text
        data['ready_to_publish'] = True
        await state.update_data(data)
        await fsmPipeline.clean_main(msg, bot, state)
        await next(msg, bot, state)


async def photo_handler(msg: Message, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("photo_handler", get_user_id(msg), current_state)

    data = await add_utility_message(msg, state, True)
    if msg.content_type is ContentType.PHOTO:
        file_id = msg.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        source_directory_path = os.path.join(Config.MEDIA_DIRECTORY_PATH, Config.ROUTE_PHOTO_DIRECTORY)
        if not os.path.exists(source_directory_path):
            os.makedirs(source_directory_path)
        file_name = uuid.uuid4().__str__() + '.jpg'
        source_path = os.path.join(source_directory_path, file_name)
        await bot.download_file(file_path, source_path)

        if not os.path.exists(source_path):
            await step_info(msg, state, bot, text="Не получилось скачать фотографию",
                            step_info_type=StepInfoType.Utility
                            )
        else:
            data[Fields.PHOTO] = os.path.join(Config.ROUTE_PHOTO_DIRECTORY, file_name)
            await state.update_data(data)
            await next(msg, bot, state)
    else:
        await fsmPipeline.info(msg, bot, state)


async def phone_number_handler(msg: Message, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("phone_number_handler", get_user_id(msg), current_state)

    data = await add_utility_message(msg, state, True)

    if msg.content_type is ContentType.TEXT:
        phone_number = phonenumbers.parse(msg.text)
        if phonenumbers.is_valid_number(phone_number):
            data[Fields.PHONE_NUMBER] = msg.text
            await state.update_data(data)
            await next(msg, bot, state)
        else:
            await step_info(msg, state, bot, text="Не корректный номер телефона, повторите еще раз",
                            step_info_type=StepInfoType.Utility
                            )
    elif msg.content_type is ContentType.CONTACT:
        data[Fields.PHONE_NUMBER] = msg.contact.phone_number
        await state.update_data(data)
        await next(msg, bot, state)


async def handle_accept_info(ctx: CallbackQuery, callback_data: NavMarkupCD, bot: Bot, state: FSMContext, alchemy_session):
    current_state = await state.get_state()
    log_handler("handle_accept_info", get_user_id(ctx), current_state)

    if callback_data.nav_type == "PUBLISH":
        data = await state.get_data()
        trip = await add_new_trip(data, alchemy_session)
        await send_route_on_moderation(ctx, trip.id, bot, state)
    elif callback_data.nav_type == "RESTART":
        await start(ctx)
    elif callback_data.nav_type == "CANCEL":
        await state.clear()
        await step_info(ctx, state, bot, text="Заполнение информации о поездке было отменено",
                        step_info_type=StepInfoType.Utility
                        )


async def form_handlers(ctx: CallbackQuery, callback_data: FormCD, bot: Bot, state: FSMContext, alchemy_session):
    current_state = await state.get_state()
    log_handler("form_handlers", get_user_id(ctx), current_state)

    data = await state.get_data()
    if data.get('ready_to_publish', None) and callback_data.type == 'PUBLISH':
        data = await state.get_data()
        trip = await add_new_trip(data, alchemy_session)
        await send_route_on_moderation(ctx, trip.id, bot, state)
    elif callback_data.type == 'CHANGE':
        data['ready_to_publish'] = False
        await state.update_data(data)
        await form_info(ctx, bot, state)
        await fsmPipeline.move_to(ctx, bot, state, fsmPipeline.pipeline[0].state)
    elif callback_data.type == 'CANCEL':
        await fsmPipeline.clean(ctx, bot, state)
        await fsmPipeline.clean_main(ctx, bot, state)
        await bot.delete_message(get_chat_id(ctx), message_id=ctx.message.message_id)
        await state.clear()


async def add_proxy_point_handler(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    proxy_points_count = sum(1 for point in data['address_points'] if point.startswith('address'))
    data['address_points'].append(f'address_{proxy_points_count + 1}')
    tasks = [state.update_data(data), address_pipeline.info(ctx, bot, state)]
    await asyncio.gather(*tasks)


async def accept(ctx: Any, bot: Bot, state: FSMContext):
    await next(ctx, bot, state)


async def skip(ctx: Any, bot: Bot, state: FSMContext):
    if await state.get_state() == RoutePrivate.COMMENTARY.state:
        data = await state.get_data()
        data['ready_to_publish'] = True
        await state.update_data(data)
        await fsmPipeline.clean_main(ctx, bot, state)

    await fsmPipeline.clean(ctx, bot, state)
    await fsmPipeline.next(ctx, bot, state)


async def next(ctx: Any, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("next", get_user_id(ctx), current_state)
    field = MapRouteStateToField.get(state, None)

    if current_state == RoutePrivate.COMMENTARY.state:
        await fsmPipeline.clean_main(ctx, bot, state)
        await state.update_data(ready_to_publish=True)

    if field:
        data = await state.get_data()
        if data.get(field, None):
            await fsmPipeline.clean(ctx, bot, state)
            await fsmPipeline.next(ctx, bot, state)
            await form_info(ctx, bot, state)
    else:
        await fsmPipeline.clean(ctx, bot, state)
        await fsmPipeline.next(ctx, bot, state)
        await form_info(ctx, bot, state)


async def remove_proxy_point(ctx: CallbackQuery, callback_data: NavMarkupCD, bot: Bot, state: FSMContext):
    data = await state.get_data()

    if not callback_data.key.startswith('address'):
        raise Exception(f'Address with key {callback_data.key} cannot be deleted')

    proxy_address_keys = [key for key in data['address_points'] if key.startswith('address')]
    proxy_address_keys.remove(callback_data.key)
    data.pop(callback_data.key, None)

    for idx, proxy_address_key in enumerate(proxy_address_keys):
        new_proxy_key = f'address_{idx + 1}'
        data[new_proxy_key] = data.pop(proxy_address_key, None)
        proxy_address_keys[idx] = new_proxy_key

    data['address_points'] = proxy_address_keys
    await state.update_data(data)
    await address_pipeline.prev(ctx, bot, state)


async def prev(ctx: Any, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("prev", get_user_id(ctx), current_state)
    if current_state == RoutePrivate.WRITE_ADDRESS.state:
        await fsmPipeline.clean(ctx, bot, state)
        await address_pipeline.prev(ctx, bot, state)
    else:
        await fsmPipeline.clean(ctx, bot, state)
        await fsmPipeline.prev(ctx, bot, state)


async def remove(ctx: Any, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    log_handler("remove", get_user_id(ctx), current_state)

    field = MapRouteStateToField[await state.get_state()]
    data = await state.get_data()
    data[field] = None
    await state.update_data(data)
    await fsmPipeline.clean(ctx, bot, state)
    await fsmPipeline.info(ctx, bot, state)
    await form_info(ctx, bot, state)


async def start(ctx: Any, bot: Bot, state: FSMContext):
    await state.clear()
    data = await state.get_data()
    data['user_id'] = get_user_id(ctx)
    data['full_name'] = ctx.from_user.full_name
    data['ready_to_publish'] = False
    await state.update_data(data)
    await form_info(ctx, bot, state)
    await fsmPipeline.move_to(ctx, bot, state, fsmPipeline.pipeline[0].state)


async def get_info(message: Message, bot: Bot, state: FSMContext):
    print(await state.get_state())
    await fsmPipeline.move_to(message, bot, state, RoutePrivate.ACCEPT_ROUTE)


async def handle_wrong_message(msg: Message, state):
    await add_utility_message(msg, state, True)


async def add_utility_message(msg: Message, state, update=False):
    data = await state.get_data()
    utility_ids = await add_item_list(state, msg.message_id, UTILITY_MESSAGE_IDS)
    data[UTILITY_MESSAGE_IDS] = utility_ids
    if update:
        await state.update_data(data)
    return data


async def add_item_list(state, item, key) -> List[Any]:
    data = await state.get_data()
    array = data.get(key, [])
    if not array:
        array = []
    if item in array:
        array.remove(item)
    else:
        array.append(item)
    return array


def setup(dp: Dispatcher):
    dp.message.register(start, commands="add_trip")
    dp.message.register(get_info, commands="help")

    skip_reply = ('Пропустить', next)
    remove_inline = (NavMarkupCD.filter(F.nav_type == "REMOVE"), remove)
    accept_inline = (NavMarkupCD.filter(F.nav_type == "CONFIRM"), next)
    add_proxy_point = (NavMarkupCD.filter(F.nav_type == "PROXY_POINT"), add_proxy_point_handler)
    prev_inline = (NavMarkupCD.filter(F.nav_type == "BACK"), prev)
    next_inline = (NavMarkupCD.filter(F.nav_type == "NEXT"), next)
    skip_inline = (NavMarkupCD.filter(F.nav_type == "SKIP"), skip)
    return_to_address = (NavMarkupCD.filter(F.nav_type == "BACK_TO_ADDRESS"), prev)
    remove_proxy = (NavMarkupCD.filter(F.nav_type == "REMOVE"), remove_proxy_point)

    address_pipeline.set_pipeline([
        step_types.CallbackStep(state=RoutePrivate.PICK_ADDRESS, handler=pick_route_handler,
                                info_handler=pick_route_point,
                                filters=[PickAddressCD.filter()],
                                inline_navigation_handler=[next_inline, add_proxy_point, prev_inline]
                                ),
        step_types.MessageStep(state=RoutePrivate.WRITE_ADDRESS, handler=address_handler,
                               filters=[F.content_type.in_({ContentType.TEXT})],
                               info_handler=address_info,
                               inline_navigation_handler=[return_to_address, remove_proxy]
                               ),
        step_types.CallbackStep(state=RoutePrivate.CONFIRM_ADDRESS, handler=address_confirm_handler,
                                info_handler=confirm_address_info,
                                filters=[ConfirmTownCD.filter()]
                                )
    ])

    juridical_status = step_types.CallbackStep(state=RoutePrivate.JURIDICAL_STATUS, handler=juridical_status_handler,
                                info_handler=juridical_status_info,
                                filters=[JuridicalStatusCD.filter()],
                                inline_navigation_handler=[prev_inline, next_inline, remove_inline, skip_inline]
                                )

    company_name = step_types.MessageStep(state=RoutePrivate.COMPANY_NAME, handler=company_name_handler,
                               info_handler=company_name_info,
                                            filters=[F.content_type.in_({ContentType.TEXT})],
                                step_filter=DataValueFilter(key=Fields.JURIDICAL_STATUS, value=JuridicalStatus.IndividualEntrepreneur),
                               inline_navigation_handler=[prev_inline, next_inline, remove_inline, skip_inline]
                               )

    contact_name = step_types.MessageStep(state=RoutePrivate.CONTACT_NAME, handler=contact_name_handler,
                                          info_handler=contact_name_info,
                                          filters=[F.content_type.in_({ContentType.TEXT})],
                                          step_filter=DataValueFilter(key=Fields.JURIDICAL_STATUS, value=JuridicalStatus.Individual),
                                          inline_navigation_handler=[prev_inline, next_inline, remove_inline, skip_inline])

    departure_date_pipeline.set_pipeline([
        step_types.CallbackStep(state=RoutePrivate.PICK_DATE_ID, handler=pick_date_handler,
                                info_handler=pick_date_info,
                                filters=[PickDateCD.filter()],
                                inline_navigation_handler=[next_inline, prev_inline],
                                ),
        step_types.CallbackStep(state=RoutePrivate.SELECT_DATE, handler=select_date_handler,
                                info_handler=select_date_info,
                                filters=[SimpleCalendarCD.filter()],
                                ),
    ]
    )

    commentary = step_types.MessageStep(state=RoutePrivate.COMMENTARY, handler=commentary_handler,
                                        info_handler=commentary_info,
                                        filters=[F.content_type.in_({ContentType.TEXT})],
                                        inline_navigation_handler=[prev_inline, next_inline, remove_inline, skip_inline]
                                        )

    payment_type = step_types.CallbackStep(state=RoutePrivate.PAYMENT_TYPE, handler=payment_type_handler,
                                           info_handler=payment_type_info,
                                           filters=[PaymentCD.filter()],
                                           inline_navigation_handler=[prev_inline, next_inline, remove_inline]
                                           )

    service_type = step_types.CallbackStep(state=RoutePrivate.SELECT_SERVICE, handler=service_handler,
                                           info_handler=service_info,
                                           filters=[ServiceTypeCD.filter()],
                                           inline_navigation_handler=[next_inline, remove_inline]
                                           )

    photo = step_types.MessageStep(state=RoutePrivate.PHOTO, handler=photo_handler,
                                   info_handler=photo_info,
                                   filters=[F.content_type.in_({ContentType.PHOTO})],
                                   inline_navigation_handler=[prev_inline, next_inline, remove_inline, skip_inline])

    phone_number = step_types.MessageStep(state=RoutePrivate.PHONE_NUMBER, handler=phone_number_handler,
                                          info_handler=phone_number_info,
                                          filters=[F.content_type.in_({ContentType.TEXT, ContentType.CONTACT})],
                                          reply_navigation_handlers=[skip_reply],
                                          inline_navigation_handler=[prev_inline, next_inline, remove_inline, skip_inline]
                                          )

    accept_route = step_types.CallbackStep(state=RoutePrivate.ACCEPT_ROUTE, handler=form_handlers,
                                           info_handler=form_info,
                                           filters=[FormCD.filter()],
                                          )

    fsmPipeline.set_pipeline([
        service_type,
        address_pipeline,
        departure_date_pipeline,
        juridical_status,
        contact_name,
        company_name,
        phone_number,
        payment_type,
        photo,
        commentary,
        accept_route
    ])
    fsmPipeline.build(dp)

    dp.message.register(handle_wrong_message, RouteFilter())
    dp.callback_query.register(form_handlers, FormCD.filter())
    # dp.callback_query.register(next)
