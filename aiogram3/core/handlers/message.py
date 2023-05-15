from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from core.utils.simple_func import *
from core.keyboards.inline import *
from core.keyboards.reply import *
from core.utils.database import *


# Функция для обработки /start
async def cmd_start(message: Message, bot: Bot):
    await set_default_commands(bot)
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


# Функция для обработки /help
async def cmd_help(message: [Message, CallbackQuery], bot: Bot):
    text = f'Я понимаю эти команды:\n'\
           f'/start\n/help\n/developer\n/manage\n'\
           f'Для получения погоды напишите желаемый регион.\n'\
           f'Для получения погоды в установленном регионе нажми "погода"'
    if type(message) is CallbackQuery:
        await message.answer()
        await bot.send_message(
            message.message.chat.id,
            text=text,
            parse_mode='',
            reply_markup=get_weather_button())  # Этот текст получит пользователь
    elif type(message) is Message:
        await bot.send_message(
            message.chat.id,
            text=text,
            parse_mode='',
            reply_markup=get_weather_button())


# Функция для обработки /manage
async def cmd_manage(message: Message):
    await message.answer(text=f'Выберите опцию:', reply_markup=menu())


# Функция для обработки /developer
async def cmd_developer(message: Message, bot: Bot):
    await bot.send_message(
        message.chat.id,
        text='<strong>@w1thoutiq</strong>',
        reply_markup=admin(), parse_mode='HTML'
    )


# Функция для обработки /message
async def cmd_message(message: Message, bot: Bot):
    cur.execute("SELECT id FROM base")
    for user_id in cur.fetchall():
        user_id = user_id[0]
        try:
            await get_weather_for_cities(call=message, bot=bot)
            cur.execute("SELECT active FROM base WHERE id =?", (user_id,))
            if int(cur.fetchone()[0]) == 0:
                cur.execute(f"UPDATE base SET active = {1} WHERE id =?", (user_id,))
                con.commit()
            cur.execute("UPDATE base SET active = 0 WHERE id =?", (user_id,))
        except Exception as e:
            print(e)
            con.commit()
    await message.answer("Рассылка завершена")


# Функция для обработки текста "Погода"
async def weather(message: Message):  # Выводим данные погоды для установленного города
    cur.execute(f"SELECT city FROM base WHERE id={message.from_user.id}")
    cities = cur.fetchone()[0].split(', ')
    await message.answer(text='Для какого региона показать погоду?',
                         reply_markup=weather_btn(cities))


async def call_alerts_message(message: Message, bot: Bot):
    await alerts_message(bot=bot)


# state=StateAlerts.subscribe
async def second_step_alert(message: Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.clear()
        await message.answer(f'Главное меню', reply_markup=menu())
    else:
        city = message.text.capitalize()
        try:  # Обработка ошибки если такого региона не существует
            if await get_weather(city) is None:
                raise ValueError
            cur.execute(f"REPLACE INTO alerts_base(id, username, city) VALUES ("
                        f'"{message.from_user.id}",'
                        f'"{message.from_user.username}",'
                        f'"{city}");')
            con.commit()
            data= await state.get_data()
            call = data.get('call')
            await call.message.edit_text(
                text='Вы подписаны на рассылку 🎉',
                reply_markup=menu()
            )
            await state.clear()
        except ValueError:
            await message.reply(f'Что-то пошло не так! \U0001F915'
                                f'\nНапишите "отмена", если передумали',
                                reply_markup=cancel())
        finally:
            await message.delete()


# state=StateSet.city
async def set_city(message: Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.clear()
        await message.answer(f'Главное меню', reply_markup=menu())
    else:
        city = message.text.capitalize()
        try:  # Обработка ошибки если такого региона не существует
            if await get_weather(city) is None:
                raise ValueError
            await state.update_data(city=city)
            await message.answer(text=f'Что ты хочешь сделать с этим регионом?', reply_markup=add_city_menu())
        except ValueError:
            await message.reply(f'Что-то пошло не так! \U0001F915'
                                f'\nНапишите "отмена", если передумали', reply_markup=cancel())


# Обработка любого текста, если есть город, тогда вернет погоду пользователю
async def unknown_message_text(message: Message):
    try:
        city = message.text.capitalize()
        await message.answer(
            text=await get_weather(city),
            parse_mode='HTML'
        )
    except Exception as e:
        print(e)
        await message.reply(f'\U0001F915 Страна или регион указан неверно!')


# Обработка любого типа сообщений, что-бы избежать лишних ошибок
async def unknown_message(message: Message):
    await message.reply(f'Я не знаю что с этим делать, но напоминаю,\n'
                        f'что вы можете использовать команду /help',
                        parse_mode='Markdown', reply_markup=mark())




