from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher import FSMContext
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import CallbackQuery
from aiogram import types
from requests import get
from main import dp, bot
from Keyboards import *
from database import cur, con
from filters import *

# scheduler = AsyncIOScheduler()
# scheduler.add_job(get_weather,x  'cron', day_of_week='mon-sun', hour=09, minute=00, end_date='2025-10-13')
# И затем scheduler.start(), только перед стартом пуллинга.
# Рабочий вариант, проверено. Если сделать привязку к бд, то задачи можно добавлять «на горячую».


class _State(StatesGroup):
    city = State()


class StateAlerts(StatesGroup):
    subscribe = State()


@dp.message_handler(commands=['start'])  # Декоратор для команды /start
async def send_welcome(message: types.Message):  # Функция для обработки /start
    await set_default_commands()
    cur.execute("SELECT id FROM base")
    if message.from_user.id not in [i[0] for i in cur.fetchall()]:
        cur.execute("INSERT INTO base VALUES (?,?,?,?)",
                    (message.from_user.username, message.from_user.id, None, 1))
        con.commit()
        await message.answer(
            f'Привет, ***{message.from_user.first_name}*** \U0001F609 !\n'
            f'Я Telegram-бот для получения погоды в любом регионе. '
            f'Для получения всех команд, которые я понимаю, нажмите "help".'
            f'\nИли пропишите команду /help.\n',
            parse_mode='Markdown',
            reply_markup=mark())
        await bot.send_message(message.chat.id,
                               f'Вижу ты тут впервые, '
                               f'напишите "/manage" для того что бы установить регион'
                               f' для получения погоды.'
                               f'\nТак же ты можешь написать любой регион, '
                               f'а я отправлю погоду в этом регионе \U000026C5',
                               parse_mode='')
    else:
        await bot.send_message(
            message.chat.id,
            f'Привет, ***{message.from_user.first_name}*** \U0001F609!\n'
            f'Я тебя помню!\n'
            f'Нажми "help" для ознакомления с командами.\n'
            f'Напиши регион для получения погоды \U000026C5',
            reply_markup=mark(),
            parse_mode='Markdown')
        await message.answer('Если у тебя уже выставлен регион просто нажми "Погода"',
                             reply_markup=get_weather_button())


@dp.callback_query_handler(text='help')
@dp.message_handler(commands=['help', 'помощь'])  # Обработка команды /help
async def send_help(message):
    text = f'Я понимаю эти команды:\n'\
           f'/start\n/help\n/developer\n/manage\n'\
           f'Для получения погоды напишите желаемый регион.\n'\
           f'Для получения погоды в установленном регионе нажми "погода"'
    if type(message) is types.CallbackQuery:
        await message.answer()
        await bot.send_message(
            message.message.chat.id,
            text=text,
            parse_mode='',
            reply_markup=get_weather_button())  # Этот текст получит пользователь
    elif type(message) is types.Message:
        await bot.send_message(
            message.chat.id,
            text=text,
            parse_mode='',
            reply_markup=get_weather_button())


@dp.message_handler(commands=['manage'])  # Декоратор для команды /manage
async def manage_menu(message: types.Message):
    await message.answer(text=f'Выберите опцию:', reply_markup=set_city_menu())


@dp.message_handler(commands=['developer'])  # Вывод команды /developer
async def send_developer(message: types.Message):
    await bot.send_message(message.chat.id, text='<strong>@w1thoutiq</strong>',
                           reply_markup=admin(), parse_mode='HTML')


# Только для администратора. Рассылка погоды для пользователей и их установленных городов
@dp.message_handler(IDFilter(790528433), commands=['message'])
async def send_message(message: types.Message):
    cur.execute("SELECT id FROM base")
    for user_id in cur.fetchall():
        user_id = user_id[0]
        try:
            await get_weather_for_cities(message)
            cur.execute("SELECT active FROM base WHERE id =?", (user_id,))
            if int(cur.fetchone()[0]) == 0:
                cur.execute(f"UPDATE base SET active = {1} WHERE id =?", (user_id,))
                con.commit()
            cur.execute("UPDATE base SET active = 0 WHERE id =?", (user_id,))
        except:
            con.commit()
    await message.answer("Рассылка завершена")


@dp.message_handler(Text(equals='Погода', ignore_case=True))
async def weather(message: types.Message):  # Выводим данные погоды для установленного города
    cur.execute(f"SELECT city FROM base WHERE id={message.from_user.id}")
    cities = cur.fetchone()[0].split(', ')
    await message.answer(text='Для какого региона показать погоду?',
                         reply_markup=weather_btn(cities))


@dp.callback_query_handler(Text(startswith='alerts_'))
async def call_alerts(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['call'] = call
    await call.answer()
    action = call.data.split('alerts_')[1]
    if action == 'unsubscribe':
        cur.execute(f'DELETE FROM alerts_base WHERE id={call.from_user.id}')
        con.commit()
        await call.message.edit_text(text='Удалил вас из рассылки', reply_markup=set_city_menu())
    elif action == 'subscribe':
        await first_step_for_alert(call)
    elif action == 'cancel':
        await call.message.edit_text(text='Главное меню', reply_markup=set_city_menu())


@dp.message_handler(content_types='text', state=StateAlerts.subscribe)
async def second_step_alert(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer(f'Главное меню', reply_markup=set_city_menu())
    else:
        city = message.text.capitalize()
        try:  # Обработка ошибки если такого региона не существует
            if await get_weather(city) is None:
                raise ValueError
            cur.execute(f"REPLACE INTO alerts_base(id, username, city) VALUES ("
                        f"'{message.from_user.id}',"
                        f"'{message.from_user.username}',"
                        f"'{city}')")
            con.commit()
            async with state.proxy() as data:
                call = data['call']
            await bot.edit_message_text(
                message_id=call.message.message_id,
                chat_id=call.message.chat.id,
                text='Вы подписаны на рассылку 🎉',
                reply_markup=set_city_menu())
            await state.finish()
        except ValueError:
            await message.reply(f'Что-то пошло не так! \U0001F915'
                                f'\nНапишите "отмена", если передумали',
                                reply_markup=cancel())
        finally:
            await message.delete()


@dp.message_handler(content_types='text', state=_State.city)
async def set_city(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer(f'Главное меню', reply_markup=set_city_menu())
    else:
        city = message.text.capitalize()
        try:  # Обработка ошибки если такого региона не существует
            if await get_weather(city) is None:
                raise ValueError
            async with state.proxy() as data:
                data['city'] = city
            await message.answer(text=f'Что ты хочешь сделать с этим регионом?', reply_markup=add_city_menu())
        except ValueError:
            await message.reply(f'Что-то пошло не так! \U0001F915'
                                f'\nНапишите "отмена", если передумали', reply_markup=cancel())


# Обработка любого текста, если есть город, тогда вернет погоду пользователю
@dp.message_handler(content_types=['text'])
async def unknown_message_text(message: types.Message):
    try:
        city = message["text"].capitalize()
        await bot.send_message(
            message.chat.id,
            text=await get_weather(city),
            parse_mode='HTML'
        )
    except:
        await message.reply(f'\U0001F915 Страна или регион указан неверно!')


# @dp.message_handler(CorrectTime(), content_types='any')
# async def correct_time_msg(message):
#     await get_weather_for_cities(message)


@dp.message_handler(content_types='any')  # Обработка любого типа сообщений, что-бы избежать лишних ошибок
async def unknown_message(message: types.Message):
    await message.reply(f'Я не знаю что с этим делать, но напоминаю,\n'
                        f'что вы можете использовать команду /help',
                        parse_mode='Markdown', reply_markup=mark())


# callbacks


@dp.callback_query_handler(Text(startswith='weather_'))
async def weather_with_button(call: CallbackQuery):
    await call.answer()
    city = call.data.split('weather_')[1]
    await get_weather(city)
    if city == 'cancel':
        await bot.delete_message(message_id=call.message.message_id,
                                 chat_id=call.from_user.id)
    elif city == 'all':
        await get_weather_for_cities(call)
    else:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=await get_weather(city),
                               parse_mode='HTML')


@dp.callback_query_handler(Text(startswith='city_'))
async def city_kb(call: CallbackQuery):
    await call.answer()
    city = call.data.split('city_')[1]
    if city == 'cancel':
        await bot.delete_message(message_id=call.message.message_id,
                                 chat_id=call.from_user.id)
    else:
        cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
        cities = cur.fetchone()[0].replace(city + ', ', '')
        cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)",
                    (call.from_user.username, call.from_user.id, cities, 1,))
        con.commit()
        cities = cities.split(', ')
        await bot.edit_message_text(message_id=call.message.message_id,
                                    chat_id=call.from_user.id,
                                    text=f'Вы удалили регион {city}\n'
                                         f'Какой еще регион хотите удалить?',
                                    reply_markup=get_button_with_city(cities))


@dp.callback_query_handler(Text(startswith='menu_'))
async def call_city(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['message_id'] = call.message.message_id
    await call.answer()
    action = call.data.split('menu_')[1]
    if action == 'change':
        cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
        city = cur.fetchone()[0][:-2].split(', ')
        await bot.send_message(chat_id=call.from_user.id,
                               text=f'Ваши регионы:',
                               reply_markup=get_button_with_city(city))
    elif action == 'add':
        await first_set_city(call)
    elif action == 'my_city':
        await my_city(call)
    elif action == 'alerts':
        await call.message.edit_text(text="Меню рассылки",
                                     reply_markup=menu_of_alerts())


@dp.callback_query_handler(Text(startswith='kb_'), state=_State.city)
async def kb_set(call, state: FSMContext):
    await call.answer()
    action = call.data.split('kb_')[1]
    async with state.proxy() as data:
        city = data['city']
    if action == 'add':
        cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
        cities = cur.fetchone()[0]
        if (city + ', ') in cities:
            await bot.edit_message_text(chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        text=f'Этот город уже есть в списке')
        else:
            cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
            cities = cur.fetchone()[0] + city + ', '
            cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)",
                        (call.from_user.username, call.from_user.id, cities, 1,))
            await bot.edit_message_text(chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        text=f'Город добавлен')
        con.commit()
    elif action == 'set':
        cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)", (
            call.from_user.username, call.from_user.id, city+', ', 1,))
        con.commit()
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    text=f'Город установлен!\nВаш регион: {city}\n')
    await state.finish()


# @dp.callback_query_handler(Text(startswith='alerts_'))
# async def call_alerts(call: CallbackQuery, state: FSMContext):
#     await call.answer()
#     action = call.data.split('alerts_')[1]
#     if action == 'unsubscribe':
#         cur.execute(f'DELETE FROM alerts_base WHERE id={call.from_user.id}')
#         con.commit()
#         await call.message.edit_text(text='Удалил вас из рассылки', reply_markup=set_city_menu())
#     elif action == 'subscribe':
#         async with state.proxy() as data:
#             data['message_id'] = call.message.message_id
#             data['chat_id'] = call.message.chat.id
#         await first_step_for_alert(call)
#     elif action == 'cancel':
#         await call.message.edit_text(text='Главное меню', reply_markup=set_city_menu())


# functions


async def my_city(message):  # Обычный вывод установленного города
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


async def first_set_city(message):
    await bot.send_message(
        chat_id=message.message.chat.id,
        text=f'Отправь свой населенный пункт')
    await _State.city.set()


async def get_weather_for_cities(call):
    cur.execute(f'SELECT city FROM base WHERE id={call.from_user.id}')
    cities = cur.fetchone()[0].split(', ')[:-1:]
    if type(call) is types.CallbackQuery:
        for city in cities:
            await bot.send_message(chat_id=call.message.chat.id,
                                   text=await get_weather(city), parse_mode='HTML',
                                   reply_markup=get_weather_button())
    elif type(call) is types.Message:
        message = call
        if type(call) is types.CallbackQuery:
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


async def first_step_for_alert(call):
    await call.message.edit_text(text=f'Отправь регион для рассылки')
    await StateAlerts.subscribe.set()


# scheduler.add_job(get_weather_for_cities, 790528433, day_of_week='mon-sun', hour=23, minute=15, end_date='2025-10-13')


async def set_default_commands() -> bot.set_my_commands:
    return await bot.set_my_commands(
        commands=[
            types.BotCommand('start', 'Запуск бота'),
            types.BotCommand('manage', 'Управление'),
            types.BotCommand('help', 'Все то, что умеет бот'),
            types.BotCommand('developer', 'Посмотреть разработчика'),
        ],
        scope=types.BotCommandScopeDefault(), )


async def alerts_message():
    try:
        cur.execute(f"SELECT id FROM alerts_base")
        users = [user[0] for user in cur.fetchall()]
        for user in users:
            cur.execute(f'SELECT city FROM alerts_base WHERE id={user}')
            city = cur.fetchone()[0]
            await bot.send_message(
                chat_id=user,
                text=f'Вы подписались на рассылку\n'
                     f'{await get_weather(city)}',
                parse_mode='HTML'
            )
        await bot.send_message(
            chat_id=790528433,
            text="Рассылка завершена",
            parse_mode='HTML'
        )
    except:
        pass


from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime as dt, timedelta


scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

scheduler.add_job(alerts_message, trigger='date', run_date=dt.now()+timedelta(seconds=1))

scheduler.add_job(alerts_message, trigger='cron', hour='07', minute='00', start_date=dt.now())

scheduler.add_job(alerts_message, trigger='cron', hour='13', minute='00', start_date=dt.now())

scheduler.add_job(alerts_message, trigger='cron', hour='17', minute='00', start_date=dt.now())
