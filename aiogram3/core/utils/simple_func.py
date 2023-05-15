from requests import get
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types import BotCommand, BotCommandScopeDefault
from core.settings import settings
from core.utils.database import *
from core.keyboards.inline import *
from core.keyboards.reply import *


async def my_city(message: [Message, CallbackQuery], bot: Bot):  # Обычный вывод установленного города
    cur.execute(f"SELECT city FROM base WHERE id={message.from_user.id}")
    city = cur.fetchone()[0].split(', ')
    if city == 'None' or len(city) == 0:
        await bot.send_message(message.message.chat.id,
                               f'Регион не установлен.')
    else:
        await bot.send_message(
            chat_id=message.message.chat.id,
            text=f'Установленные регионы:',
            reply_markup=weather_btn(city))


async def get_weather_for_cities(call: [Message, CallbackQuery], bot: Bot):
    cur.execute(f'SELECT city FROM base WHERE id={call.from_user.id}')
    cities = cur.fetchone()[0].split(', ')[:-1:]
    if type(call) is CallbackQuery:
        for city in cities:
            await bot.send_message(chat_id=call.message.chat.id,
                                   text=await get_weather(city), parse_mode='HTML',
                                   reply_markup=get_weather_button())
    elif type(call) is Message:
        message = call
        if type(call) is CallbackQuery:
            for city in cities:
                await bot.send_message(chat_id=message.chat.id,
                                       text=await get_weather(city), parse_mode='HTML',
                                       reply_markup=get_weather_button())
    return


async def get_weather(city):
    try:
        url = 'https://api.openweathermap.org/data/2.5/weather'
        api_of_weather = '352c751a80237a51813f0ae93d864822'
        params = {'APPID': api_of_weather,
                  'q': city,
                  'units': 'metric',
                  'lang': 'ru'}
        result = get(url, params=params).json()
        info = result['main']['temp'], result['main']['feels_like'], result['weather'][0]['description'], result['name']
        message_text = f'Погода в регионе <strong>{info[3]}</strong>:\n' \
                       f'<em><strong>{info[0]} °C, ощущается как {info[1]}°C, {info[2]}</strong></em>'
        return message_text
    except KeyError:
        return


# Установка меню
async def set_default_commands(bot: Bot):
    return await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description='Запуск бота'),
            BotCommand(command='manage', description='Управление'),
            BotCommand(command='developer', description='Посмотреть разработчика'),
            BotCommand(command='help', description='Все то, что умеет бот'),

        ],
        scope=BotCommandScopeDefault(), )


async def alerts_message(bot: Bot):
    count = 0
    try:
        cur.execute(f"SELECT id FROM alerts_base")
        users = [user[0] for user in cur.fetchall()]
        for user in users:
            try:
                cur.execute(f'SELECT city FROM alerts_base WHERE id={user}')
                city = cur.fetchone()[0]
                await bot.send_message(
                    chat_id=user,
                    text=await get_weather(city),
                    parse_mode='HTML'
                )
                count += 1
                cur.execute("SELECT active FROM base WHERE id =?", (user,))
                if int(cur.fetchone()[0]) == 0:
                    cur.execute(f"UPDATE base SET active = {1} WHERE id =?", (user,))
                    con.commit()
            except Exception as e:
                print(e)
                cur.execute("UPDATE base SET active = 0 WHERE id =?", (user,))
                con.commit()
    finally:
        await bot.send_message(
            chat_id=settings.bots.admin_id,
            text=f"Рассылка завершена:\n\rЧисло сообщений: {count}",
            parse_mode='HTML'
        )
