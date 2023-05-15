from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def remove_kb():
    return ReplyKeyboardRemove()


def cancel():
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    return kb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_weather_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text='Погода')
    return kb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )