from aiogram.filters import BaseFilter
from aiogram.types import Message
from core.settings import settings


class IsAdmin(BaseFilter):
    def __call__(self, message: Message) -> bool:
        try:
            return message.from_user.id == settings.bots.admin_id
        except Exception as e:
            print(e)
            return False