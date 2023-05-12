import logging
import filters
from os import getenv as env
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from datetime import datetime as dt
from aiogram import Dispatcher, Bot
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
#
#
# scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=env('weather_bot'))
dp = Dispatcher(bot, storage=MemoryStorage())

from Functions import *

# scheduler.add_job(alerts_message, trigger='date', run_date=dt.now().second+1)


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp)
