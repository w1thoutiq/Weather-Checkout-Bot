import logging
from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv as env
from aiogram import Dispatcher, Bot

logging.basicConfig(level=logging.INFO)
bot = Bot(token=env('weather_bot'))
dp = Dispatcher(storage=MemoryStorage())

from Functions import *


if __name__ == '__main__':
    dp.startup.register(startup)
    dp.shutdown.register(shutting_off)
    scheduler.start()
    dp.start_polling(bot)
