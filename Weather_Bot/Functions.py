from requests import get
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from main import dp, bot
from Keyboards import *
from database import *


class _State(StatesGroup):
    city = State()


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
        await bot.send_message(message.from_user.id,
                               f'Вижу ты тут впервые, '
                               f'напишите "/set_city" для того что бы установить основной регион'
                               f' для получения погоды.'
                               f'\nНапишите "/set_city"'
                               f'\nТак же ты можешь написать любой регион, '
                               f'а я отправлю погоду в этом регионе \U000026C5',
                               parse_mode='')
    else:
        await bot.send_message(
            message.from_user.id,
            f'Привет, ***{message.from_user.first_name}*** \U0001F609!\n'
            f'Я тебя помню!\n'
            f'Нажми "help" для ознакомления с командами.\n'
            f'Напиши регион для получения погоды \U000026C5',
            reply_markup=mark(),
            parse_mode='Markdown')
        await message.answer('Если у тебя уже выставлен регион просто нажми "Погода"',
                             reply_markup=get_weather_button())


@dp.message_handler(commands=['help'])  # Обработка команд /help
async def send_help(message):
    await bot.send_message(
        message.from_user.id,
        f'Я понимаю эти команды:\n'
        f'/start\n/help\n/developer\n/manage\n'
        f'Для получения погоды напишите желаемый регион.\n'
        f'Для получения погоды в установленном регионе нажми "погода"',
        parse_mode='',
        reply_markup=get_weather_button())  # Этот текст получит пользователь


@dp.message_handler(commands=['manage'])  # Декоратор для команды /manage
async def manage_menu(message: types.Message):
    await message.answer(text=f'Выберите опцию:', reply_markup=set_city_menu())


@dp.message_handler(commands=['developer'])  # Вывод команды /developer
async def send_developer(message: types.Message):
    await bot.send_message(message.from_user.id, text='<strong>Я тут!\n'
                                                      '@w1thoutiq</strong>',
                           reply_markup=admin(), parse_mode='HTML')


# Только для администратора. Рассылка погоды для пользователей и их установленных городов
@dp.message_handler(IDFilter(790528433), commands=['message'])
async def send_message(message: types.Message):
    cur.execute("SELECT id FROM base")
    for user_id in cur.fetchall():
        user_id = user_id[0]
        try:
            await get_weather_for_cities(user_id)
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


@dp.message_handler(content_types='text', state=_State.city)
async def set_city(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer(f'Главное меню')
    else:
        city = message.text.capitalize()
        try:  # Обработка ошибки если такого региона не существует
            if await get_weather(city) is None:
                raise ValueError
            async with state.proxy() as data:
                data['city'] = city
            await message.answer(text=f'Что ты хочешь сделать с этим регионом?', reply_markup=add_city_menu())
        except ValueError:
            await message.reply(f'Что-то пошло не так!\U0001F915'
                                f'\nНапишите "отмена", если передумали', reply_markup=cancel())


# Обработка любого текста, если есть город, тогда вернет погоду пользователю
@dp.message_handler(content_types=['text'])
async def unknown_message_text(message: types.Message):
    try:
        city = message["text"].capitalize()
        await bot.send_message(message.from_user.id,
                               text=await get_weather(city), parse_mode='HTML')
    except:
        await message.reply(f'\U0001F915 Страна или регион указан неверно!')


@dp.message_handler()  # Обработка любого типа сообщений, что-бы избежать лишних ошибок
async def unknown_message(message: types.Message):
    await message.reply(f'Я не знаю что с этим делать, но напоминаю,\n'
                        f'что вы можете использовать команду /help',
                        parse_mode='Markdown', reply_markup=mark())


#callbacks


@dp.callback_query_handler(text='help')  # Обработка callback из кнопки help в сообщении /start
async def help_in_welcome(call: CallbackQuery):
    await call.answer()
    await send_help(call)


@dp.callback_query_handler(Text(startswith='weather_'))
async def weather_with_button(call:CallbackQuery):
    await call.answer()
    city = call.data.split('weather_')[1]
    await get_weather(city)
    if city == 'cancel':
        await bot.delete_message(message_id=call.message.message_id,
                                 chat_id=call.from_user.id)
    elif city == 'all':
        await get_weather_for_cities(call.from_user.id)
    else:
        await bot.send_message(chat_id=call.from_user.id,
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
        cities = cur.fetchone()[0].replace(city + ', ' , '')
        cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)",
                    (call.from_user.username, call.from_user.id, cities, 1,))
        con.commit()
        cities = cities.split(', ')
        await bot.edit_message_text(message_id=call.message.message_id,
                                    chat_id=call.from_user.id,
                                    text=f'Вы удалили регион {city}:\n'
                                         f'Какой еще регион хотите удалить?',
                                    reply_markup=get_button_with_city(cities))


@dp.callback_query_handler(Text(startswith='menu_'))
async def call_city(call: CallbackQuery):
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
    else:
        await my_city(call)


@dp.callback_query_handler(Text(startswith='kb_'), state=_State.city)
async def kb_set(call, state: FSMContext):
    await call.answer()
    action = call.data.split('kb_')[1]
    async with state.proxy() as data:
        city = data['city']
    if action == 'add':
        cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
        cities = cur.fetchone()[0] + city + ', '
        cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)",
                    (call.from_user.username, call.from_user.id, cities, 1,))
        con.commit()
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    text=f'Город добавлен')
    elif action == 'set':
        cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)", (
            call.from_user.username, call.from_user.id, city+', ', 1,))
        con.commit()
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                               text=f'Город установлен!\nВаш регион: {city}\n')
    await state.finish()


#functions


async def my_city(message):  # Обычный вывод установленного города
    cur.execute(f"SELECT city FROM base WHERE id={message.from_user.id}")
    city = cur.fetchone()[0].split(', ')
    if city == 'None' or len(city) == 0:
        await bot.send_message(message.from_user.id,
                               f'Регион не установлен.')
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'Установленные регионы:',
            reply_markup=weather_btn(city)
        )


async def first_set_city(message):  # Функция для обработки /set_city
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f'Отправь свой населенный пункт')
    await _State.city.set()


async def get_weather_for_cities(id_of_user):
    cur.execute(f'SELECT city FROM base WHERE id={id_of_user}')
    cities = cur.fetchone()[0].split(', ')[:-1:]
    for city in cities:
        await bot.send_message(chat_id=id_of_user,
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


async def set_default_commands() -> bot.set_my_commands:
    return await bot.set_my_commands(
        commands=[
            types.BotCommand('start', 'Запуск бота'),
            types.BotCommand('manage', 'Управление'),
            types.BotCommand('developer', 'Посмотреть разработчика'),
            types.BotCommand('help', 'Все то, что умеет бот'),

        ],
        scope=types.BotCommandScopeDefault(), )
