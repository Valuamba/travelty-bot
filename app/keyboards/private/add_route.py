import re

from aiogram.types import KeyboardButtonPollType

from app.handlers.service.helpers.departure_date import get_departure_date_ids, DEPARTURE_DATE_KEY
from app.models.sql.enums import JuridicalStatusLocals, PaymentTypeLocales, ServiceTypeLocals, JuridicalStatus, \
    ServiceType, PaymentType
from app.utils.markup_constructor import ReplyMarkupConstructor
from aiogram.dispatcher.filters.callback_data import CallbackData

from app.utils.markup_constructor import InlineMarkupConstructor
from app.utils.markup_constructor.refactor import refactor_keyboard


class JuridicalStatusCD(CallbackData, prefix='jur_status'):
    status: int


class ConfirmTownCD(CallbackData, prefix='confirm_town'):
    status: str


class PickDateCD(CallbackData, prefix='add_route'):
    date_id: int


class PaymentCD(CallbackData, prefix='add_route'):
    payment_type: int


class NavMarkupCD(CallbackData, prefix='nav'):
    nav_type: str


class ServiceTypeCD(CallbackData, prefix='add_route'):
    service_type: int


class AddRouteInlineMarkup(InlineMarkupConstructor):
    def get_service_markup(self, services=[]):
        actions = []
        for service in ServiceType:
            actions.append({'text': ServiceTypeLocals[service] + ' ✔' if service in services else ServiceTypeLocals[service],
                            'callback_data': ServiceTypeCD(service_type=service).pack()}
                           )

        schema = [2, 2, 1, 1]
        self._add_accept(actions, schema)
        self._add_back(actions, schema)
        return self.markup(actions, schema)

    def get_payment_markup(self):
        actions = [
            {'text': PaymentTypeLocales[PaymentType.WithoutPayment],
             'callback_data': PaymentCD(payment_type=PaymentType.WithoutPayment).pack()},
            {'text': PaymentTypeLocales[PaymentType.WithPayment],
             'callback_data': PaymentCD(payment_type=PaymentType.WithPayment).pack()},
            {'text': PaymentTypeLocales[PaymentType.NotDecided],
             'callback_data': PaymentCD(payment_type=PaymentType.NotDecided).pack()},
        ]
        schema = [1, 1, 1]
        return self.markup(actions, schema)

    def get_confirm_town_markup(self):
        actions = [
            {'text': 'Да', 'callback_data': ConfirmTownCD(status='yes').pack()},
            {'text': 'Нет', 'callback_data': ConfirmTownCD(status='no').pack()},
        ]
        schema = [1, 1]
        return self.markup(actions, schema)

    def get_pick_date_markup(self, data: dict):
        departure_keys_ids = get_departure_date_ids(data)
        actions = []
        schema = []

        for ind in range(3):
            if ind in departure_keys_ids:
                departure_date = data[DEPARTURE_DATE_KEY + str(ind)]
                actions.append({'text': f'Изменить дату {ind + 1} - {departure_date}', 'callback_data': PickDateCD(date_id=ind).pack()})
            else:
                actions.append({'text': f'Выбрать дату {ind + 1}', 'callback_data': PickDateCD(date_id=ind).pack()})
            schema.append(1)

        if len(departure_keys_ids) > 0:
            self._add_accept(actions, schema)

        return self.markup(actions, schema)

    def get_juridical_status_markup(self):
        actions = []
        for e in JuridicalStatus:
            actions.append({'text': JuridicalStatusLocals[e.value],
                            'callback_data': JuridicalStatusCD(status=e.value).pack()}
                           )
        schema = refactor_keyboard(1, actions)
        self._add_back(actions, schema)
        return self.markup(actions, schema)

    def _add_accept(self, actions, schema):
        if len(actions) > 0:
            schema.append(1)
            actions.append(
                {'text': 'Подтвердить', 'callback_data': NavMarkupCD(nav_type='confirm')})

    def _add_back(self, actions, schema):
        if len(actions) > 0:
            schema.append(1)
            actions.append(
                {'text': 'Назад', 'callback_data': NavMarkupCD(nav_type='back')})


class RouteReplyMarkup(ReplyMarkupConstructor):
    def get_back_markup(self):
        schema = [1, 1]
        actions = [
            {'text': 'Назад'},
        ]
        return self.markup(actions, schema, resize_keyboard=True)

    def get_optional_step_markup(self):
        schema = [1, 1]
        actions = [
            {'text': 'Назад'},
            {'text': 'Пропустить'},
        ]
        return self.markup(actions, schema, resize_keyboard=True)

    def get_phone_number_keyboard(self):
        actions = [
            {'text': 'Отправить номер телефона', 'contact': True},
        ]
        return self.markup(actions, refactor_keyboard(1, actions), resize_keyboard=True)