from aiogram.dispatcher.filters.callback_data import CallbackData
from beanie import PydanticObjectId

from app.utils.markup_constructor import InlineMarkupConstructor


class ExampleMarkup(InlineMarkupConstructor):
    class CD(CallbackData, prefix='test'):
        number: str

    def get(self):
        schema = [3, 2]
        actions = [
            {'text': '1', 'callback_data': self.CD(number='1')},
            {'text': '2', 'callback_data': self.CD(number='2').pack()},
            {'text': '3', 'callback_data': '3'},
            {'text': '4', 'callback_data': self.CD(number='4').pack()},
            {'text': '6', 'callback_data': '6'},
        ]
        return self.markup(actions, schema)


class LoupeCD(CallbackData, prefix='radius'):
    radius: int
    callback_id: str

class LoupeMarkup(InlineMarkupConstructor):
    def get(self, callback_id: PydanticObjectId, radius: int = 150):
        delta = 30
        actions = []
        if radius > 0:
            actions.append({'text': f'-{delta}', 'callback_data': LoupeCD(radius=radius - delta, callback_id=str(callback_id)).pack()})
        else:
            actions.append({'text': '⏺', 'callback_data': '_'})

        actions.append({'text': radius, 'callback_data': '_'})

        if radius < 500:
            actions.append({'text': f'+{delta}', 'callback_data': LoupeCD(radius=radius + delta, callback_id=str(callback_id)).pack()})
        else:
            actions.append({'text': '⏺', 'callback_data': '_'})

        schema = [3]
        return self.markup(actions, schema)