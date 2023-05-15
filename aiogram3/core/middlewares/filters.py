import sys
from abc import ABC

from aiogram.filters import BaseFilter
from aiogram.types import Message

sys.path.append('C:\\Users\\withoutiq\\PycharmProjects\\WeatherCheckoutBot\\New-Weather-bot\\')
from core.settings import settings


class IsAdmin(BaseFilter, ABC):
    @staticmethod
    def check(message: Message):
        return message.from_user.id == settings.bots.admin_id