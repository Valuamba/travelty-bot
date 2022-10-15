
from enum import IntEnum
from app.utils.markup_constructor import InlineMarkupConstructor
from aiogram.dispatcher.filters.callback_data import CallbackData


class StartMenuType(IntEnum):
    CREATE_ROUTE = 1

class StartMenuCD(CallbackData, prefix='start-menu'):
    type: StartMenuType


class MainInlineMarkup(InlineMarkupConstructor):
    
    def get_start_command_keyboard(self):
        actions = [
            { 'text': '🚕 Создать объявление', 'callback_data': StartMenuCD(type=StartMenuType.CREATE_ROUTE).pack() },
            { 'text': '❓ Обучающее видео (1 мин.)', 'url': 'https://www.youtube.com/watch?v=r0JG-qRMDVw&ab_channel=Valentin'}
        ]
    
        return self.markup(actions, [1])