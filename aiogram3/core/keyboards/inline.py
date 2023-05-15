from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def menu_of_alerts():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Подписаться', callback_data='alerts_subscribe'))
    builder.add(InlineKeyboardButton(text='Отписаться', callback_data='alerts_unsubscribe'))
    builder.add(InlineKeyboardButton(text=f'Назад', callback_data=f'alerts_cancel'))
    builder.adjust(2, 1)
    return builder.as_markup()


def get_button_with_city(cities) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=city, callback_data=f'city_{city}')] for city in cities]
    buttons.append([InlineKeyboardButton(text=f'Назад', callback_data=f'city_cancel')])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


def weather_btn(cities):
    markup = InlineKeyboardBuilder()
    for city in cities:
        markup.add(InlineKeyboardButton(text=city, callback_data=f'weather_{city}'))
    markup.adjust(1)
    markup.add(InlineKeyboardButton(text=f'Все регионы', callback_data=f'weather_all'),
               InlineKeyboardButton(text=f'Назад', callback_data=f'weather_cancel'))
    return markup.as_markup()


def menu():
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text='Удалить регионы', callback_data='menu_change'))
    markup.add(InlineKeyboardButton(text='Добавить регионы', callback_data='menu_add'))
    markup.add(InlineKeyboardButton(text='Посмотреть ваши регионы', callback_data='menu_my_city'))
    markup.add(InlineKeyboardButton(text='Рассылка', callback_data='menu_alerts'))
    markup.adjust(2)
    return markup.as_markup()


def add_city_menu():
    markup = InlineKeyboardBuilder()
    markup.add(
        InlineKeyboardButton(text='Установить единственным', callback_data='kb_set'),
        InlineKeyboardButton(text='Добавить регион', callback_data='kb_add'))
    return markup.as_markup()


def admin():
    buttons = InlineKeyboardBuilder()
    buttons.add(InlineKeyboardButton(text='Вавилон',
                                     url='https://t.me/w1thoutiq'))
    return buttons.as_markup()


def mark():
    markup = InlineKeyboardBuilder()  # Создаём макеты для отображения кнопок
    markup.add(InlineKeyboardButton(text='help', callback_data='help'))  # Добавляем кнопку help
    return markup.as_markup()