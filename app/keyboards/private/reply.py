from aiogram.types import KeyboardButtonPollType
from app.utils.markup_constructor import ReplyMarkupConstructor


class RouteReplyMarkup(ReplyMarkupConstructor):
    def get_back_markup(self):
        schema = [1]
        actions = [
            {'text': 'Назад'}
        ]
        return self.markup(actions, schema, resize_keyboard=True)
