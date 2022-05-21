import asyncio
from typing import Union, Any, List
from aiogram import Bot, Dispatcher, Router, types
from aiogram.dispatcher.event.handler import HandlerType
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiohttp import ClientSession
from app.handlers.fsm.step_types import MessageStep, CallbackStep, UTILITY_MESSAGE_IDS
from app.utils.update import get_chat_id


class FSMPipeline:
    pipeline: List[Any]

    def set_pipeline(self, pipeline: []):
        self.pipeline = pipeline

    async def next(self, ctx: Any, bot: Bot, state: FSMContext, only_state=False):
        route_len = len(self.pipeline)
        for idx, step_pipeline in enumerate(self.pipeline):
            current_state = await state.get_state()
            if (isinstance(step_pipeline, FSMPipeline) and any(
                    step.state.state == current_state for step in step_pipeline.pipeline
                    )) \
                    or ((isinstance(step_pipeline, MessageStep) or isinstance(step_pipeline, CallbackStep
                                                                              )) and step_pipeline.state.state == current_state):
                if idx != route_len - 1:
                    next_pipeline = self.pipeline[idx + 1]
                    if isinstance(next_pipeline, FSMPipeline):
                        next_pipeline = next_pipeline.pipeline[0]
                    if not only_state:
                        await next_pipeline.info_handler(ctx, bot=bot, state=state)
                    await state.set_state(next_pipeline.state)
                else:
                    raise Exception("Cannot move pointer to next state, because you are in last state")
                return

    async def clean(self, ctx: Any, bot: Bot, state: FSMContext):
        data = await state.get_data()
        message_ids = data.get(UTILITY_MESSAGE_IDS, None)
        if message_ids:
            tasks = []
            for id in message_ids:
                tasks.append(bot.delete_message(get_chat_id(ctx), id))
            data[UTILITY_MESSAGE_IDS] = []
            await state.update_data(data)
            try:
                await asyncio.gather(*tasks)
            except:
                print("Error when deleting message")


    async def info(self, ctx: Any, bot: Bot, state: FSMContext):
        for idx, step_pipeline in enumerate(self.pipeline):
            current_state = await state.get_state()
            if (isinstance(step_pipeline, FSMPipeline) and any(
                    step.state.state == current_state for step in step_pipeline.pipeline
            )) \
                    or ((isinstance(step_pipeline, MessageStep) or isinstance(step_pipeline, CallbackStep
                                                                              )) and step_pipeline.state.state == current_state):
                current_pipeline = self.pipeline[idx]
                await current_pipeline.info_handler(ctx, bot=bot, state=state)

    async def move_to(self, ctx: Any, bot: Bot, state: FSMContext, next_state: State):
        for idx, step_pipeline in enumerate(self.pipeline):
            if (isinstance(step_pipeline, FSMPipeline) and any(
                    step.state.state == next_state.state for step in step_pipeline.pipeline
                    )) \
                    or ((isinstance(step_pipeline, MessageStep) or isinstance(step_pipeline, CallbackStep
                                                                              )) and step_pipeline.state.state == next_state.state):
                if isinstance(step_pipeline, FSMPipeline):
                    step_pipeline = step_pipeline.pipeline[0]
                await step_pipeline.info_handler(ctx, bot=bot, state=state)
                await state.set_state(step_pipeline.state)
                return

        raise Exception(f"State {next_state} was not found in pipeline")

    async def prev(self, ctx: Any, bot: Bot, state: FSMContext, only_state=False):
        for idx, step_pipeline in enumerate(self.pipeline):
            current_state = await state.get_state()
            if (isinstance(step_pipeline, FSMPipeline) and any(
                    step.state.state == current_state for step in step_pipeline.pipeline
                    )) \
                    or ((isinstance(step_pipeline, MessageStep) or isinstance(step_pipeline, CallbackStep
                                                                              )) and step_pipeline.state.state == current_state):
                if idx > 0:
                    prev_pipeline = self.pipeline[idx - 1]
                    if isinstance(prev_pipeline, FSMPipeline):
                        prev_pipeline = prev_pipeline.pipeline[0]
                    if not only_state:
                        await prev_pipeline.info_handler(ctx, bot=bot, state=state)
                    await state.set_state(prev_pipeline.state)
                else:
                    raise Exception("Cannot move pointer to prev state, because you are in first state")
                return

    def build(self, router: Router):
        for idx, state_pipeline in enumerate(self.pipeline):
            if isinstance(state_pipeline, FSMPipeline):
                state_pipeline.build(router)
            else:
                if len(state_pipeline.reply_navigation_handlers) > 0:
                    for reply_handler in state_pipeline.reply_navigation_handlers:
                        router.message.register(reply_handler[1], text=reply_handler[0], state=state_pipeline.state)
                if len(state_pipeline.inline_navigation_handler) > 0:
                    for inline_handler in state_pipeline.inline_navigation_handler:
                        router.callback_query.register(inline_handler[1], inline_handler[0], state=state_pipeline.state)

                if isinstance(state_pipeline, MessageStep):
                    router.message.register(state_pipeline.handler, state=state_pipeline.state)
                elif isinstance(state_pipeline, CallbackStep):
                    router.callback_query.register(state_pipeline.handler, state_pipeline.filter,
                                                   state=state_pipeline.state
                                                   )
