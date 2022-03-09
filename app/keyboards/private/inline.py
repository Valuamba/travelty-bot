from aiogram.dispatcher.filters.callback_data import CallbackData

from app.models.route import PaymentType, PaymentTypeLocales, ServiceType, ServiceTypeLocals
from app.utils.markup_constructor import InlineMarkupConstructor


class ConfirmTownMarkup(InlineMarkupConstructor):
    class CD(CallbackData, prefix='confirm_town'):
        status: str

    def get(self):
        actions = [
            {'text': 'Да', 'callback_data': self.CD(status='yes').pack()},
            {'text': 'Нет', 'callback_data': self.CD(status='no').pack()},
        ]
        schema = [1, 1]
        return self.markup(actions, schema)


class GetPaymentMarkup(InlineMarkupConstructor):
    class CD(CallbackData, prefix='add_route'):
        payment_type: int

    def get(self):
        actions = [
            {'text': PaymentTypeLocales[PaymentType.WithoutPayment],
             'callback_data': self.CD(payment_type=PaymentType.WithoutPayment).pack()},
            {'text': PaymentTypeLocales[PaymentType.WithPayment],
             'callback_data': self.CD(payment_type=PaymentType.WithPayment).pack()},
            {'text': PaymentTypeLocales[PaymentType.NotDecided],
             'callback_data': self.CD(payment_type=PaymentType.NotDecided).pack()},
        ]
        schema = [1, 1, 1]
        return self.markup(actions, schema)


class GetServiceMarkup(InlineMarkupConstructor):
    class CD(CallbackData, prefix='add_route'):
        service_type: int

    def get(self, services=[]):
        actions = []
        schema = []
        for service in ServiceType:
            schema.append(1)
            actions.append({
                'text': ServiceTypeLocals[service] + '✔️' if service in services else ServiceTypeLocals[service],
                'callback_data': self.CD(service_type=service).pack()
            })
        if len(services) > 0:
            schema.append(1)
            actions.append({'text': 'Подтвердить', 'callback_data': 'accept'})
        return self.markup(actions, schema)
