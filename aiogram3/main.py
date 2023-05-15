import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime as dt

from aiogram import Dispatcher, F, Bot
from aiogram.filters import Command

from core.handlers.basic import startup, shutting_off
from core.utils.simple_func import alerts_message
from core.handlers.callback import *
from core.handlers.message import *
from core.settings import settings
from core.utils.states import *
from core.middlewares.filters import IsAdmin


async def start():

    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - "
               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    # Сообщения по расписанию
    scheduler.add_job(alerts_message, trigger='cron', hour='07', minute='00', start_date=dt.now(), kwargs={'bot':bot})
    scheduler.add_job(alerts_message, trigger='cron', hour='13', minute='00', start_date=dt.now(), kwargs={'bot':bot})
    scheduler.add_job(alerts_message, trigger='cron', hour='17', minute='00', start_date=dt.now(), kwargs={'bot':bot})

    # Функции для запуска и завершения работы бота
    dp.startup.register(startup)
    dp.shutdown.register(shutting_off)

    # Обработка сообщений
    dp.message.register(cmd_start, Command(commands=['start']))
    dp.message.register(cmd_help, Command(commands=['help']))
    dp.message.register(cmd_developer, Command(commands=['developer']))
    dp.message.register(cmd_manage, Command(commands=['manage']))
    dp.message.register(cmd_message, IsAdmin() and Command(commands=['message']))
    dp.message.register(weather, F.text.lower() == 'погода')
    dp.message.register(second_step_alert, F.text and StateAlerts.subscribe)
    dp.message.register(set_city, F.text and StateSet.city)
    dp.message.register(unknown_message_text, F.text)
    dp.message.register(unknown_message, F.any)

    # Обработка callback-ов
    dp.callback_query.register(weather_with_button, F.data.startswith('weather_'))
    dp.callback_query.register(cmd_help, F.data == 'help')
    dp.callback_query.register(city_kb, F.data.startswith('city_'))
    dp.callback_query.register(call_city, F.data.startswith('menu_'))
    dp.callback_query.register(kb_set, F.data.startswith('kb_') and StateSet.city)
    dp.callback_query.register(call_alerts, F.data.startswith('alerts_'))

    try:
        scheduler.start()
        await dp.start_polling(bot)

    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(start())