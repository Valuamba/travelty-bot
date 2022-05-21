from aiogram import types, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommandScopeChat

from app.config import Config
from app.models import UserModel, UserRoles


async def set_commands(bot: Bot) -> None:
    # users = UserModel.find(UserModel.role != UserRoles.admin)
    users = await UserModel.find().to_list()
    for user in users:
        try:
            await bot.set_my_commands(
                [
                    types.BotCommand(command="start", description="Запустить бота"),
                    types.BotCommand(command="add_trip", description="Создать объявление"),
                ],
                BotCommandScopeChat(chat_id=user.id)
            )
        except TelegramBadRequest:
            print(f'Chat {user.id}')

    # for admin in Config.ADMINS:
    #     await bot.set_my_commands(
    #         [
    #             types.BotCommand(command="amount", description="Количество юзеров в бд"),
    #             types.BotCommand(command="chat_amount", description="Количество групп в бд"),
    #             types.BotCommand(command="chat_users_amount", description="Количество пользователей во всех группах"),
    #             types.BotCommand(command="exists_amount", description="Количество живых юзеров"),
    #             types.BotCommand(command="broadcast", description="Рассылка по всем юзерам"),
    #             types.BotCommand(command="users_file", description='Записать юзеров в файл'),
    #         ],
    #         BotCommandScopeChat(chat_id=admin),
    #     )
