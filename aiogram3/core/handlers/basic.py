import sys
from aiogram import Bot

sys.path.append('C:\\Users\\withoutiq\\PycharmProjects\\WeatherCheckoutBot\\New-Weather-bot\\')
from core.settings import settings


async def startup(bot: Bot):
    return await bot.send_message(
        chat_id=settings.bots.admin_id,
        text="Бот запущен!"
    )


async def shutting_off(bot: Bot):
    return await bot.send_message(
        chat_id=settings.bots.admin_id,
        text="Бот выключен!"
    )