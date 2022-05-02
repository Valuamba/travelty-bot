from typing import Any
from aiogram import Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from geopy import Nominatim

from app.keyboards.private.add_route import AddRouteInlineMarkup, RouteReplyMarkup
from app.keyboards.simple_calendar import SimpleCalendar
from app.models.sql.enums import JuridicalStatus
from app.utils.update import get_chat_id


async def departure_town_info(ctx: Any, bot: Bot, state: FSMContext):
    text = "Введите город отправления"
    await send_info(ctx, bot, text=text)


async def arrival_town_info(ctx: Any, bot: Bot, state: FSMContext):
    text = "Введите город прибытия"
    await send_info(ctx, bot, text=text)


async def confirm_arrival_town_info(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    address = data['arrival_address']
    text = f"Введенная вами локация: %s" % address['display_name']
    await send_info(ctx, bot, text=text,
                           reply_markup=AddRouteInlineMarkup().get_confirm_town_markup())


async def confirm_departure_town_info(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    address = data['departure_address']
    text = f"Введенная вами локация: %s" % address['display_name']
    await send_info(ctx, bot, text=text,
                           reply_markup=AddRouteInlineMarkup().get_confirm_town_markup())


async def juridical_status_info(ctx: Any, bot: Bot, state: FSMContext):
    text = f"Выберите ваш юридический статус:"
    await send_info(ctx, bot, text=text,
                           reply_markup=AddRouteInlineMarkup().get_juridical_status_markup()
                           )


async def company_name_info(ctx: Any, bot: Bot, state: FSMContext):
    text = f"Введите наименование ИП:"
    await send_info(ctx, bot, text=text)


async def contact_name_info(ctx: Any, bot: Bot, state: FSMContext):
    text = f"Введите контактное имя:"
    await send_info(ctx, bot, text=text)


async def service_info(ctx: Any, bot: Bot, state: FSMContext):
    services = (await state.get_data()).get('services', [])
    text = f"Выберите одну или несколько предоставляемых услуг:"
    await send_info(ctx, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_service_markup(services)
                    )


async def payment_type_info(ctx: Any, bot: Bot, state: FSMContext):
    text = f"Выберите тип вознаграждения:"
    await send_info(ctx, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_payment_markup()
                    )


async def pick_date_info(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    text = f"Выберите 1-3 даты, в которые вы будете совершать поездку/поездки:"
    await send_info(ctx, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_pick_date_markup(data)
                    )


async def select_date_info(ctx: Any, bot: Bot, state: FSMContext):
    text = f"Выберите дату:"
    await send_info(ctx, bot, text=text,
                    reply_markup=await SimpleCalendar().start_calendar(bot, state)
                    )


async def commentary_info(ctx: Any, bot: Bot, state: FSMContext):
    text = "Оставьте дополнительный комментарий (макс. 150 символов):"
    await send_info(ctx, bot, text=text)


async def photo_info(ctx: Any, bot: Bot, state: FSMContext):
    text = "Прикрепите фотографию вашего авто, настоятельно рекомендуем сркывать номер автомобиля, в целях безопасности."
    await send_info(ctx, bot, text=text)


async def phone_number_info(ctx: Any, bot: Bot, state: FSMContext):
    text = 'Введите номер телефона или нажмите на кнопку ниже'
    await send_info(ctx, bot, text=text,
                           reply_markup=RouteReplyMarkup().get_phone_number_keyboard()
                           )

async def accept_result(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()

    text = \
        f"<b>Комментарий: </b>{data['commentary']}" + \
        f"<b>Адрес отправления: </b>{data['departure_address']}" + \
        f"<b>Адрес прибытия: </b>{data['arrival_address']}" + \


    juridical_status = data['juridical_status']
    if juridical_status == JuridicalStatus.IndividualEntrepreneur:
        text += "<b>Наименование компании: </b>{data['company_name']}"
    elif juridical_status == JuridicalStatus.Individual:
        text += f"<b>Контактное лицо: </b>{data['contact_name']}"

    phone_number = data.get('phone_number', None)
    if phone_number:
        text += f"<b>Номер телефона: </b>{phone_number}"

async def send_info(ctx: Any, bot: Bot, text, reply_markup=None):
    if isinstance(ctx, CallbackQuery):
        await bot.edit_message_text(chat_id=get_chat_id(ctx), message_id=ctx.message.message_id, text=text,
                                    reply_markup=reply_markup)
    elif isinstance(ctx, Message):
        await bot.send_message(chat_id=get_chat_id(ctx), text=text, reply_markup=reply_markup)