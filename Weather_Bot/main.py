import logging
from os import environ as env
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot

logging.basicConfig(level=logging.INFO)

bot = Bot(token=env.get('weather_bot'))
dp = Dispatcher(bot, storage=MemoryStorage())

from Functions import *

if __name__ == '__main__':
    executor.start_polling(dp)

