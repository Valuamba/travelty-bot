import base64
import datetime
import os
from typing import Any
from aiogram import Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, BufferedInputFile, InputFile, FSInputFile
from geopy import Nominatim

from app.config import Config
from app.handlers.fsm.bot_utility import safe_edit
from app.handlers.fsm.fsm_utility import step_info, StepInfoType
from app.handlers.fsm.step_types import UTILITY_MESSAGE_IDS, MAIN_STEP_MESSAGE_ID
from app.handlers.service.helpers.constants import Fields
from app.handlers.service.helpers.departure_date import get_departure_date_values
from app.handlers.service.helpers.trip_mapper import map_data_to_trip_str, map_trip_to_str
from app.keyboards.private.add_route import AddRouteInlineMarkup, RouteReplyMarkup
from app.keyboards.simple_calendar import SimpleCalendar
from app.models.sql.enums import JuridicalStatus, ServiceTypeLocals, PaymentTypeLocales, TripStatus
from app.models.sql.service import Trip
from app.utils.route_mapping import map_route_data_to_str, map_route_to_form, map_trip_to_form
from app.utils.update import get_chat_id


async def juridical_status_info(ctx: Any, bot: Bot, state: FSMContext):
    juridical_status = (await state.get_data()).get(Fields.JURIDICAL_STATUS, None)
    text = f"[4/9] 👨‍⚖ Выберите ваш юридический статус:"
    await step_info(ctx, state, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_juridical_status_markup(juridical_status))


async def company_name_info(ctx: Any, bot: Bot, state: FSMContext):
    company_name = (await state.get_data()).get(Fields.COMPANY_NAME, None)
    conditon = company_name is not None
    text = f"[5/9] 🌐 Введите наименование ИП:"

    if conditon:
        text += f"\n\n📝Введенное наименование: {company_name}"

    help = "🔎 Введенное вами наименование будет опубликовано вместе с анкетой."
    await step_info(ctx, state, bot, text=_resolve_text(text, help),
                    reply_markup=AddRouteInlineMarkup().company_name_markup(conditon))


async def contact_name_info(ctx: Any, bot: Bot, state: FSMContext):
    company_name = (await state.get_data()).get(Fields.CONTACT_NAME, None)
    conditon = company_name is not None
    text = f"🤳 Введите имя контактного лица:"
    if conditon:
        text += f"\n\n📝Введенное контактное лицо: {company_name}"
    help = "🔎 Введенное вами имя будет опубликовано вместе с анкетой."
    await step_info(ctx, state, bot, text=_resolve_text(text, help),
                    reply_markup=AddRouteInlineMarkup().contact_name_markup(conditon))


async def service_info(ctx: Any, bot: Bot, state: FSMContext):
    services = (await state.get_data()).get('services', [])
    text = f"[1/9] 📣 Выберите одну или несколько оказываемых вами услуг:"
    await step_info(ctx, state, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_service_markup(services))


async def payment_type_info(ctx: Any, bot: Bot, state: FSMContext):
    payment_type = (await state.get_data()).get(Fields.PAYMENT_TYPE, None)
    text = f"[7/9] 🧮 Выберите тип вознаграждения:"
    await step_info(ctx, state, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_payment_markup(payment_type), update_type=CallbackQuery)


async def pick_route_point(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    data.setdefault('address_points', ['departure_address', 'arrival_address'])
    text = f"[2/9] 🛣 Заполните пункт отправления и пункт прибытия:"
    await step_info(ctx, state, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_pick_address_markup(data))
    await state.update_data(data)


async def pick_date_info(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    text = f"[3/9] 📆 Укажите 1-3 даты, в которые вы будете совершать поездку(ки) по заданному маршруту:"
    await step_info(ctx, state, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_pick_date_markup(data))


async def address_info(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    address_key = data['address_key']
    text = "Введите город/населенный пункт/деревню/страну."
    address = data.get(address_key, None)
    if address:
        text += f"\n\n📝Введенный ранее адрес: {address['display_name']}"
    help = "⚠️Для более точного поиска локации введите полный адрес, например: 'Брест, Беларусь'"
    await step_info(ctx, state, bot, text=_resolve_text(text, help),
                    reply_markup=AddRouteInlineMarkup().get_address_markup(address_key), update_type=CallbackQuery)


async def confirm_address_info(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    address = data['current_address']
    text = f"📍 Введенная вами локация: %s" % address['display_name']
    await step_info(ctx, state, bot, text=text,
                    reply_markup=AddRouteInlineMarkup().get_confirm_town_markup(), step_info_type=StepInfoType.Utility)


async def select_date_info(ctx: Any, bot: Bot, state: FSMContext):
    text = f"🗓 Выберите дату:"
    await step_info(ctx, state, bot, text=text,
                    reply_markup=await SimpleCalendar().start_calendar(bot, state), update_type=CallbackQuery)


async def commentary_info(ctx: Any, bot: Bot, state: FSMContext):
    commentary = (await state.get_data()).get(Fields.COMMENTARY, None)
    condition = commentary is not None
    text = "[9/9] 📎 Оставьте дополнительный комментарий:"
    if condition:
        text += f"\n\nВведенный комментарий: {commentary}"
    help = "⚠ Максимально допустимое количество символов - 150."
    await step_info(ctx, state, bot, text=_resolve_text(text, help),
                    reply_markup=AddRouteInlineMarkup().commentary_markup(condition), update_type=CallbackQuery)


async def photo_info(ctx: Any, bot: Bot, state: FSMContext):
    photo = (await state.get_data()).get(Fields.PHOTO, None)
    condition = photo is not None
    text = "[8/9] 📸 Прикрепите фотографию вашего авто."
    help = '❗ Рекомендуем не показывать номер автомобиля.'
    await step_info(ctx, state, bot, text=_resolve_text(text, help),
                    reply_markup=AddRouteInlineMarkup().photo_markup(condition), update_type=CallbackQuery)


async def phone_number_info(ctx: Any, bot: Bot, state: FSMContext):
    phone_number = (await state.get_data()).get(Fields.PHONE_NUMBER, None)
    condition = phone_number is not None
    text = '[6/9] ☎️ Введите номер телефона вручную или нажмите на кнопку ниже.'
    if condition:
        text += f"\n\n📝Введенный номер телефона: {phone_number}"
    help = '<i>🔎 Совет: нажмите на кнопку ниже или введите вручную, например +375 29 821 5478.</i>'
    await step_info(ctx, state, bot, text=text, reply_markup=AddRouteInlineMarkup().phone_number_markup(condition), update_type=CallbackQuery)
    await step_info(ctx, state, bot, text=help, reply_markup=RouteReplyMarkup().get_phone_number_keyboard(),
                    step_info_type=StepInfoType.Utility, update_type=Message, disable_notification=True)


async def accept_result_info(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    caption = map_data_to_trip_str(data)
    file_path = os.path.join(Config.MEDIA_DIRECTORY_PATH, data['photo_path'])
    await bot.send_photo(chat_id=get_chat_id(ctx),
                         photo=FSInputFile(path=file_path, filename="img"),
                         caption=caption,
                         reply_markup=AddRouteInlineMarkup().get_accept_route_markup())


async def form_info(ctx: Any, bot: Bot, state: FSMContext):
    data = await state.get_data()
    form_message = data.get('form_message', None)
    text = map_route_data_to_str(data)
    photo_path = _get_photo_path(data)
    print(f'FILE PATH: {photo_path}')
    encoded_text = base64.b64encode((text + photo_path + str(data['ready_to_publish'])).encode('utf-8'))
    if data.get('form_text', None) != encoded_text:
        await state.update_data(form_text=encoded_text)
        data["form_text"] = encoded_text
        if form_message:
            media = InputMediaPhoto(media=FSInputFile(path=photo_path, filename="img"), caption=text)
            async with safe_edit(ctx):
                await bot.edit_message_media(chat_id=get_chat_id(ctx), message_id=form_message, media=media,
                                             reply_markup=AddRouteInlineMarkup().get_form_markup(data['ready_to_publish']))
        else:
            message = await bot.send_photo(chat_id=get_chat_id(ctx),
                                 photo=FSInputFile(path=photo_path, filename="img"),
                                 caption=text,
                                 reply_markup=AddRouteInlineMarkup().get_form_markup(data['ready_to_publish'])
                                 )
            data['form_message'] = message.message_id
        await state.update_data(data)


def _get_photo_path(data):
    photo_path = data.get('photo_path', None)
    if photo_path:
        file_path = os.path.join(Config.MEDIA_DIRECTORY_PATH, data['photo_path'])
    else:
        file_path = os.path.join(os.getcwd(), 'app/assets/no_photo.jpg')
    return file_path


async def send_route_on_moderation(ctx, trip_id, bot: Bot, state: FSMContext):
    data = await state.get_data()
    caption = map_route_to_form(data)
    photo_path = _get_photo_path(data)
    async with safe_edit(ctx):
        await bot.edit_message_caption(chat_id=get_chat_id(ctx), message_id=ctx.message.message_id, caption=caption)
    await bot.send_message(chat_id=get_chat_id(ctx),
                           reply_to_message_id=ctx.message.message_id,
                           text="🔎 Форма была отправлена на модерацию. Обычно, проверка занимает 15 минут.")
    await bot.send_photo(chat_id=Config.ADMIN_CHAT,
                           photo=FSInputFile(path=photo_path, filename="img"),
                           caption=caption, reply_markup=AddRouteInlineMarkup().get_moderator_markup(get_chat_id(ctx), trip_id, ctx.message.message_id))


async def send_moderated_info(ctx, trip_status: TripStatus, chat_id, message_id, trip: Trip, bot: Bot, state: FSMContext):
    caption = map_trip_to_form(trip)
    if trip.caption_path:
        file_path = os.path.join(Config.MEDIA_DIRECTORY_PATH, trip.caption_path)
    else:
        file_path = os.path.join(os.getcwd(), Config.DEFAULT_PHOTO)

    if trip_status == TripStatus.Published:
        moderator_caption = "🔶 Маршрут был опубликован\r\n" + caption
        user_text = "🔶 Маршрут был опубликован"
        await bot.send_photo(chat_id=Config.TRAVELTY_COM_CHANNEL,
                             photo=FSInputFile(path=file_path, filename="img"),
                             caption=caption
                             )
    elif trip_status == TripStatus.Canceled:
        moderator_caption = "❌ Публикация была отклонена\r\n" + caption
        user_text = "❌ Публикация маршрута была отклонена"
    else:
        raise Exception(f"Wrong Trip status: {trip_status}")

    async with safe_edit(ctx):
        await bot.edit_message_caption(chat_id=get_chat_id(ctx), message_id=ctx.message.message_id, caption=moderator_caption)
    await bot.send_message(chat_id=chat_id, reply_to_message_id=message_id, text=user_text)


def _resolve_text(info: str, help: str):
    return info + '\n\n' + f'<i>{help}</i>'