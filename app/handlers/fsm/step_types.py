from typing import Union, Any, List
from aiogram import Bot, Dispatcher, Router, types
from aiogram.dispatcher.event.handler import HandlerType, FilterType
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery


class MessageStep:
    def __init__(self,
                 state: State,
                 handler: HandlerType,
                 info_handler: HandlerType,
                 reply_navigation_handlers = [],
                 inline_navigation_handler: HandlerType = [],
                 content_types: types.ContentType = types.ContentType.TEXT):
        self.state = state
        self.handler = handler
        self.info_handler = info_handler
        self.reply_navigation_handlers = reply_navigation_handlers
        self.inline_navigation_handler = inline_navigation_handler
        self.content_types = content_types


class CallbackStep:
    def __init__(self,
                 state: State,
                 handler: HandlerType,
                 info_handler: HandlerType,
                 filter: FilterType,
                 reply_navigation_handlers: List[HandlerType] = [],
                 inline_navigation_handler = [],
                 content_types: types.ContentType = types.ContentType.TEXT):
        self.state = state
        self.handler = handler
        self.info_handler = info_handler
        self.filter = filter
        self.reply_navigation_handlers = reply_navigation_handlers
        self.inline_navigation_handler = inline_navigation_handler
        self.content_types = content_types
