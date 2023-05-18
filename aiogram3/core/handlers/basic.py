from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
from core.settings import settings


async def startup(bot: Bot):
    await set_default_commands(bot)
    await bot.send_message(
        chat_id=settings.bots.admin_id,
        text="Бот запущен!"
    )


async def shutting_off(bot: Bot):
    return await bot.send_message(
        chat_id=settings.bots.admin_id,
        text="Бот выключен!"
    )


async def set_default_commands(bot: Bot):
    return await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description='Запуск бота'),
            BotCommand(command='manage', description='Управление'),
            BotCommand(command='help', description='Все то, что умеет бот'),
            BotCommand(command='developer', description='Посмотреть разработчика'),
        ],
        scope=BotCommandScopeDefault(), )
