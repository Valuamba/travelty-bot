import re
from typing import Tuple

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


class FormCD(CallbackData, prefix='form'):
    type: str


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
                {'text': f'{CHECKBOX_BUTTON} ' + ServiceTypeLocals[service] if services and service in services else ServiceTypeLocals[service],
                 'callback_data': ServiceTypeCD(service_type=service).pack()}
                )
        schema = refactor_keyboard(1, actions)
        self.__add_navigation_buttons(actions, schema, services and len(services) > 0, (False, False, True, True))
        return self.markup(actions, schema)

    def get_payment_markup(self, payment_type):
        actions = []
        for type in PaymentType:
            if type == payment_type:
                text = f'{PaymentTypeLocales[type]} {RADIO_BUTTON}'
            else:
                text = PaymentTypeLocales[type]
            actions.append({'text': text, 'callback_data': PaymentCD(payment_type=type).pack()})
        schema = refactor_keyboard(1, actions)
        self.__add_navigation_buttons(actions, schema, payment_type is not None)
        return self.markup(actions, schema)

    def get_address_markup(self, address_key):
        actions = [
            {'text': '⬅️ Назад', 'callback_data': NavMarkupCD(nav_type='BACK_TO_ADDRESS').pack()},
        ]

        if address_key.startswith('address'):
            self._remove(actions, key=address_key)
        return self.markup(actions, refactor_keyboard(2, actions))

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

        self.__add_navigation_buttons(actions, schema, departure_keys_ids and len(departure_keys_ids) > 0, (True, False, False, True))

        return self.markup(actions, schema)

    def company_name_markup(self, next_condition):
        actions = []
        schema = []
        self.__add_navigation_buttons(actions, schema, next_condition, (True, True, True, True))
        return self.markup(actions, schema)

    def contact_name_markup(self, next_condition):
        actions = []
        schema = []
        self.__add_navigation_buttons(actions, schema, next_condition, (True, True, True, True))
        return self.markup(actions, schema)

    def phone_number_markup(self, next_condition):
        actions = []
        schema = []
        self.__add_navigation_buttons(actions, schema, next_condition, (True, True, True, True))
        return self.markup(actions, schema)

    def commentary_markup(self, next_condition):
        actions = []
        schema = []
        self.__add_navigation_buttons(actions, schema, next_condition, (True, True, True, True))
        return self.markup(actions, schema)

    def photo_markup(self, next_condition):
        actions = []
        schema = []
        self.__add_navigation_buttons(actions, schema, next_condition, (True, True, True, True))
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
        self.__add_navigation_buttons(actions, schema, juridical_status)
        return self.markup(actions, schema)

    def get_accept_route_markup(self):
        actions = []
        actions.append({'text': '🆗 Опубликовать', 'callback_data': NavMarkupCD(nav_type='PUBLISH').pack()})
        actions.append({'text': '🔄 Начать сначала', 'callback_data': NavMarkupCD(nav_type='RESTART').pack()})
        actions.append({'text': '❌ Отмена', 'callback_data': NavMarkupCD(nav_type='CANCEL').pack()})

        return self.markup(actions, refactor_keyboard(1, actions))

    def get_form_markup(self, publish: bool = False):
        actions = []
        if publish:
            actions.append({'text': '🆗 Опубликовать', 'callback_data': FormCD(type='PUBLISH').pack()})
            actions.append({'text': '✒️Изменить', 'callback_data': FormCD(type='CHANGE').pack()})
        actions.append({'text': '❌ Удалить', 'callback_data': FormCD(type='CANCEL').pack()})

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

    def _remove(self, actions, schema = None, key=None):
        if schema:
            schema.append(1)
        actions.append(
            {'text': '🗑 Удалить', 'callback_data': NavMarkupCD(nav_type='REMOVE', key=key).pack()}
        )

    def _add_skip(self, actions, schema = None):
        if schema:
            schema.append(1)
        actions.append(
            {'text': 'Пропустить ↩', 'callback_data': NavMarkupCD(nav_type='SKIP').pack()}
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

    def __add_navigation_buttons(self, actions, schema, next_condition, display: Tuple[bool, bool, bool, bool] = (True, False, True, True), scheme_pattern: [] = None):
        row = 3
        displayed_buttons_count = 0
        if display[0]:
            self._add_back(actions)
            displayed_buttons_count += 1
        if not next_condition:
            if display[1]:
                self._add_skip(actions)
                displayed_buttons_count += 1
        else:
            if display[2]:
                self._remove(actions)
                displayed_buttons_count += 1
            if display[3]:
                self._add_next(actions)
                displayed_buttons_count += 1

        if scheme_pattern:
            schema += scheme_pattern
        else:
            if displayed_buttons_count > 0:
                schema += refactor_keyboard(row, actions[-displayed_buttons_count:])


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
