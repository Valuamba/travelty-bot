import re

from aiogram.types import KeyboardButtonPollType

from app.handlers.service.helpers.departure_date import get_departure_date_ids, DEPARTURE_DATE_KEY
from app.localization.static_locals import AddressKeysSelectAction, NumberEmojiLocale
from app.models.sql.enums import JuridicalStatusLocals, PaymentTypeLocales, ServiceTypeLocals, JuridicalStatus, \
    ServiceType, PaymentType
from app.utils.markup_constructor import ReplyMarkupConstructor
from aiogram.dispatcher.filters.callback_data import CallbackData

from app.utils.markup_constructor import InlineMarkupConstructor
from app.utils.markup_constructor.refactor import refactor_keyboard


RADIO_BUTTON = '🔘'
CHECKBOX_BUTTON = '☑'

class JuridicalStatusCD(CallbackData, prefix='jur_status'):
    status: int


class ConfirmTownCD(CallbackData, prefix='confirm_town'):
    status: str


class PickDateCD(CallbackData, prefix='add_route'):
    date_id: int


class PickAddressCD(CallbackData, prefix='add_route'):
    address_key: str


class PaymentCD(CallbackData, prefix='add_route'):
    payment_type: int


class NavMarkupCD(CallbackData, prefix='nav'):
    nav_type: str
    chat_id: int = None
    trip_id: int = None
    message_id: int = None
    key: str = None


class ChangeRouteCD(CallbackData, prefix='change_route'):
    field: str


class ServiceTypeCD(CallbackData, prefix='add_route'):
    service_type: int


class AcceptCD(CallbackData, prefix='add-route'):
    accpet_type: str


class AddRouteInlineMarkup(InlineMarkupConstructor):
    def get_service_markup(self, services=[]):
        actions = []
        for service in ServiceType:
            actions.append(
                {'text': '🔘 ' + ServiceTypeLocals[service] if service in services else ServiceTypeLocals[service],
                 'callback_data': ServiceTypeCD(service_type=service).pack()}
                )

        schema = [1, 1, 1, 1, 1, 1]

        if len(services) > 0:
            self._add_next(actions, schema)
        # self._add_back(actions, schema)
        return self.markup(actions, schema)

    def get_payment_markup(self, payment_type):
        actions = []
        schema = []
        for type in PaymentType:
            if type == payment_type:
                text = f'{PaymentTypeLocales[type]} {RADIO_BUTTON}'
            else:
                text = PaymentTypeLocales[type]
            actions.append({'text': text, 'callback_data': PaymentCD(payment_type=type).pack()})
            schema.append(1)

        self._add_back(actions)
        if payment_type:
            self._add_next(actions)
            schema += refactor_keyboard(2, actions[-2:])
        else:
            schema.append(1)
        return self.markup(actions, schema)

    def get_address_markup(self, address_key):
        actions = []
        schema = []
        self._add_back(actions, schema)
        if address_key.startswith('address'):
            self._remove(actions, schema, address_key)
            schema = [2]

        return self.markup(actions, schema)

    def get_confirm_town_markup(self):
        actions = [
            {'text': '❌ Нет', 'callback_data': ConfirmTownCD(status='no').pack()},
            {'text': '✅ Да', 'callback_data': ConfirmTownCD(status='yes').pack()},
        ]
        schema = [2]
        return self.markup(actions, schema)

    def get_pick_address_markup(self, data):
        actions = []
        schema = []
        max_proxy_points_counts = 3
        is_accept_btn_disabled = False

        def append_address_button(key):
            nonlocal is_accept_btn_disabled
            address = data.get(key, None)
            callback_data = PickAddressCD(address_key=key).pack()
            if address:
                place = address['place']
                text = f'🪄 Изменить - {place}'
                if key == 'departure_address':
                    text += ' 🔺'
                elif key == 'arrival_address':
                    text += ' 🔻'
                elif key.startswith('address'):
                    address_idx = re.search("(?<=address_)\d+", key).group(0)
                    # text += f' {NumberEmojiLocale[int(address_idx)]}'
                    text += f' ·{int(address_idx)}·'
                else:
                    raise Exception(f"Wrong address key {key}")
            else:
                if key == 'departure_address' or key == 'arrival_address':
                    is_accept_btn_disabled = True
                text = f'✍ Заполнить - {AddressKeysSelectAction[key]}'

            actions.append({'text': text, 'callback_data': callback_data})
            schema.append(1)

        address_points = data['address_points']

        append_address_button('departure_address')
        for key in [address for address in address_points if address.startswith('address')]:
            append_address_button(key)
        append_address_button('arrival_address')

        utility_actions = []
        self._add_back(utility_actions)

        if sum(1 for point in address_points if point.startswith('address')) < max_proxy_points_counts:
            utility_actions.append({'text': '➕ Добавить', 'callback_data': NavMarkupCD(nav_type='PROXY_POINT').pack()})

        if not is_accept_btn_disabled:
            self._add_next(utility_actions)

        utility_schema = refactor_keyboard(3, utility_actions)

        actions += utility_actions
        schema += utility_schema
        return self.markup(actions, schema)

    def get_pick_date_markup(self, data: dict):
        departure_keys_ids = get_departure_date_ids(data)
        actions = []
        schema = []

        for ind in range(3):
            if ind in departure_keys_ids:
                departure_date = data[DEPARTURE_DATE_KEY + str(ind)]
                actions.append({'text': f'✍ Изменить дату {ind + 1} - {departure_date}',
                                'callback_data': PickDateCD(date_id=ind).pack()}
                               )
            else:
                actions.append({'text': f'📆 Выбрать дату {ind + 1}', 'callback_data': PickDateCD(date_id=ind).pack()})
            schema.append(1)

        utility_actions = []
        self._add_back(utility_actions)
        if len(departure_keys_ids) > 0:
            self._add_next(utility_actions)

        utility_schema = refactor_keyboard(3, utility_actions)
        actions += utility_actions
        schema += utility_schema

        return self.markup(actions, schema)

    def company_name_markup(self, next_condition):
        actions = []
        schema = []

        self._add_back(actions, schema)
        if next_condition:
            self._add_next(actions, schema)
        return self.markup(actions, refactor_keyboard(2, actions))

    def contact_name_markup(self, next_condition):
        actions = []
        schema = []

        self._add_back(actions, schema)
        if next_condition:
            self._add_next(actions, schema)
        return self.markup(actions, refactor_keyboard(2, actions))

    def phone_number_markup(self, next_condition):
        actions = []
        schema = []

        self._add_back(actions, schema)
        if next_condition:
            self._add_next(actions, schema)
        return self.markup(actions, refactor_keyboard(2, actions))

    def commentary_markup(self, next_condition):
        actions = []
        schema = []

        self._add_back(actions, schema)
        if next_condition:
            self._add_next(actions, schema)
        return self.markup(actions, refactor_keyboard(2, actions))

    def photo_markup(self):
        actions = []
        schema = []

        self._add_back(actions, schema)
        return self.markup(actions, schema)

    def get_juridical_status_markup(self, juridical_status):
        actions = []
        schema = []
        for e in JuridicalStatus:
            if juridical_status == e:
                text = f'{JuridicalStatusLocals[e.value]} {RADIO_BUTTON}'
            else:
                text = f'{JuridicalStatusLocals[e.value]}'
            actions.append({'text': text, 'callback_data': JuridicalStatusCD(status=e.value).pack()})
            schema.append(1)

        self._add_back(actions)
        if juridical_status:
            self._add_next(actions)
            schema += refactor_keyboard(2, actions[-2:])
        else:
            schema.append(1)
        return self.markup(actions, schema)

    def get_accept_route_markup(self):
        actions = [
            {'text': '🆗 Опубликовать', 'callback_data': NavMarkupCD(nav_type='PUBLISH').pack()},
            {'text': '🔄 Начать сначала', 'callback_data': NavMarkupCD(nav_type='RESTART').pack()},
            {'text': '❌ Отмена', 'callback_data': NavMarkupCD(nav_type='CANCEL').pack()},
        ]
        return self.markup(actions, refactor_keyboard(1, actions))

    def get_moderator_markup(self, chat_id: int, trip_id: int, message_id: int):

        print(
            f"NavMarkup: {NavMarkupCD(nav_type='PUBLISH', chat_id=chat_id, trip_id=trip_id, message_id=message_id).pack()}"
            )

        actions = [
            {'text': '🆗 Опубликовать', 'callback_data': NavMarkupCD(nav_type='PUBLISH', chat_id=chat_id, trip_id=trip_id,
                                                                  message_id=message_id
                                                                  ).pack()},
            {'text': '❌ Отменить', 'callback_data': NavMarkupCD(nav_type='CANCEL', chat_id=chat_id, trip_id=trip_id,
                                                              message_id=message_id
                                                              ).pack()}
        ]
        return self.markup(actions, refactor_keyboard(1, actions))

    def _remove(self, actions, schema, key=None):
        schema.append(1)
        actions.append(
            {'text': '🗑 Удалить', 'callback_data': NavMarkupCD(nav_type='REMOVE', key=key).pack()}
        )

    def _add_accept(self, actions, schema = None):
        if schema:
            schema.append(1)
        actions.append(
            {'text': '✅ Подтвердить', 'callback_data': NavMarkupCD(nav_type='CONFIRM').pack()}
        )

    def _add_next(self, actions, schema = None):
        if schema:
            schema.append(1)
        actions.append(
            {'text': 'Далее  ➡', 'callback_data': NavMarkupCD(nav_type='NEXT').pack()}
        )

    def _add_back(self, actions, schema=None):
        if schema is not None:
            schema.append(1)
        actions.append(
            {'text': '⬅️ Назад', 'callback_data': NavMarkupCD(nav_type='BACK').pack()}
        )


class RouteReplyMarkup(ReplyMarkupConstructor):
    def get_back_markup(self):
        schema = [1, 1]
        actions = [
            {'text': '⬅️Назад'},
        ]
        return self.markup(actions, schema, resize_keyboard=True)

    def get_optional_step_markup(self):
        schema = [1, 1]
        actions = [
            {'text': '⬅️Назад'},
            {'text': 'Пропустить ➡'},
        ]
        return self.markup(actions, schema, resize_keyboard=True)

    def get_phone_number_keyboard(self):
        actions = [
            {'text': '☎️Отправить номер телефона', 'contact': True},
        ]
        return self.markup(actions, refactor_keyboard(1, actions), resize_keyboard=True, one_time_keyboard=True)
