from typing import Union, Any, List
from aiogram import Bot, Dispatcher, Router, types
from aiogram.dispatcher.event.handler import HandlerType, FilterType, FilterObject
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

UTILITY_MESSAGE_IDS = "utility_message_ids"
MAIN_STEP_MESSAGE_ID = "main_step_message_id"


class MessageStep:
    def __init__(self,
                 state: State,
                 handler: HandlerType,
                 info_handler: HandlerType,
                 step_filter: Any = None,
                 filters: [FilterType] = [],
                 reply_navigation_handlers = [],
                 inline_navigation_handler = [],
                 content_types: types.ContentType = types.ContentType.TEXT):
        self.state = state
        self.handler = handler
        self.filters = filters
        if step_filter:
            self.step_filter = FilterObject(step_filter)
        else:
            self.step_filter = None
        self.info_handler = info_handler
        self.reply_navigation_handlers = reply_navigation_handlers
        self.inline_navigation_handler = inline_navigation_handler
        self.content_types = content_types


class CallbackStep:
    def __init__(self,
                 state: State,
                 handler: HandlerType,
                 info_handler: HandlerType,
                 step_filter: Any = None,
                 filters: [FilterType] = [],
                 reply_navigation_handlers: List[HandlerType] = [],
                 inline_navigation_handler = [],
                 content_types: types.ContentType = types.ContentType.TEXT):
        self.state = state
        self.handler = handler
        if step_filter:
            self.step_filter = FilterObject(step_filter)
        else:
            self.step_filter = None
        self.info_handler = info_handler
        self.filters = filters
        self.reply_navigation_handlers = reply_navigation_handlers
        self.inline_navigation_handler = inline_navigation_handler
        self.content_types = content_types
