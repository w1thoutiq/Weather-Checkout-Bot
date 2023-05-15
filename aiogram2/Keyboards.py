from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove,\
    InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton


def menu_of_alerts() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardMarkup(text='Подписаться', callback_data='alerts_subscribe'),
        InlineKeyboardMarkup(text='Отписаться', callback_data='alerts_unsubscribe')
    ).add(InlineKeyboardMarkup(text=f'Назад', callback_data=f'alerts_cancel'))


def get_button_with_city(cities) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=city, callback_data=f'city_{city}') for city in cities]
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(*buttons).add(InlineKeyboardButton(text=f'Назад', callback_data=f'city_cancel'))
    return markup


def weather_btn(cities) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for city in cities:
        markup.add(InlineKeyboardButton(text=city, callback_data=f'weather_{city}'))
    markup.add(InlineKeyboardButton(text=f'Все регионы', callback_data=f'weather_all'),
               InlineKeyboardButton(text=f'Назад', callback_data=f'weather_cancel'))
    return markup


def set_city_menu() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    return markup.add(InlineKeyboardButton(text='Удалить регионы', callback_data='menu_change'),
                      InlineKeyboardButton(text='Добавить регионы', callback_data='menu_add')).add(
        InlineKeyboardButton(text='Посмотреть ваши регионы', callback_data='menu_my_city'),
        InlineKeyboardButton(text='Рассылка', callback_data='menu_alerts'))


def add_city_menu() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    return markup.add(InlineKeyboardButton(text='Установить единственным', callback_data='kb_set'),
                      InlineKeyboardButton(text='Добавить регион', callback_data='kb_add'))


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def cancel() -> ReplyKeyboardRemove:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return kb.add(KeyboardButton(text='Отмена'))


def get_weather_button() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True).add(KeyboardButton('Погода'))


def admin() -> InlineKeyboardMarkup:
    buttons = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return buttons.add(
        InlineKeyboardButton(
            text='Вавилон',
            url='https://t.me/w1thoutiq'))


def mark() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(resize_keyboard=True)  # Создаём макеты для отображения кнопок
    return markup.add(InlineKeyboardButton(text='help', callback_data='help'))  # Добавляем кнопку help
