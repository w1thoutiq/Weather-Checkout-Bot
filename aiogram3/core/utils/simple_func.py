from requests import get
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from core.settings import settings
# from core.utils.database import *
from core.keyboards.inline import *
from core.keyboards.reply import *
from core.utils.session_db import *
from core.utils.connect_db import *
from aiogram import flags


@flags.chat_action("typing")
async def my_city(message: CallbackQuery, bot: Bot):  # Обычный вывод установленного города
    try:
        with create_session() as db:
            city = db.query(User.city).where(User.id == int(message.from_user.id)).first()[0].split(', ')
            await bot.send_message(
                chat_id=message.message.chat.id,
                text=f'Установленные регионы:',
                reply_markup=weather_btn(city)
            )
    except AttributeError:
        await bot.send_message(
            chat_id=message.message.chat.id,
            text=f'У вас нету установленных регионов'
        )


@flags.chat_action("typing")
async def get_weather_for_cities(user_id: int, bot: Bot, chat_id: int):
    with create_session() as db:
        cities = db.query(User.city).where(User.id == user_id).first()[0].split(', ')
    if cities == ['']:
        return await bot.send_message(
            chat_id=chat_id,
            text='Сначала установи регионы'
        )
    if '' in cities:
        cities.remove('')
    for city in cities:
        await bot.send_message(
            chat_id=chat_id,
            text=await get_weather(city),
            parse_mode='HTML',
            reply_markup=get_weather_button()
        )
    return


def get_weather(city, for_graph=False):
    try:
        url = 'https://api.openweathermap.org/data/2.5/weather'
        api_of_weather = '352c751a80237a51813f0ae93d864822'
        params = {'APPID': api_of_weather,
                  'q': city,
                  'units': 'metric',
                  'lang': 'ru'}
        result = get(url, params=params).json()
        info = result['main']['temp'], result['main']['feels_like'], result['weather'][0]['description'], result['name']
        if for_graph is True:
            return int(info[0])
        message_text = f'Погода в регионе <strong>{info[3]}</strong>:\n' \
                       f'<em><strong>{info[0]} °C, ощущается как {info[1]}°C, {info[2]}</strong></em>'
        return message_text
    except KeyError:
        return


@flags.chat_action("typing")
async def alerts_message(bot: Bot):
    count = 0
    try:
        with create_session() as db:
            users = [int(user[0]) for user in db.query(Alert.id).all()]
            for user in users:
                try:
                    city = db.query(Alert.city).where(Alert.id == user).first()[0]
                    await bot.send_message(
                        chat_id=user,
                        text=await get_weather(city),
                        parse_mode='HTML'
                    )
                    count += 1
                    db.query(User).where(User.id == user).update(
                        {User.active: True})
                except Exception as e:
                    print(e, 'in alerts')
                    db.query(User).where(User.id == user).update(
                        {User.active: False})
    finally:
        db.commit()
        await bot.send_message(
            chat_id=settings.bots.admin_id,
            text=f"Рассылка завершена:\n\rЧисло сообщений: {count}",
            parse_mode='HTML'
        )

