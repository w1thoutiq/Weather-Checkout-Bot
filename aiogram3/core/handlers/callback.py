from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from core.utils.simple_func import *
from core.keyboards.inline import *
from core.utils.database import *
from core.utils.states import *


# startswith='weather_'
async def weather_with_button(call: CallbackQuery, bot: Bot):
    await call.answer()
    city = call.data.split('weather_')[1]
    await get_weather(city)
    if city == 'cancel':
        await bot.delete_message(message_id=call.message.message_id,
                                 chat_id=call.message.chat.id)
    elif city == 'all':
        await get_weather_for_cities(call, bot=bot)
    else:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=await get_weather(city),
                               parse_mode='HTML')


# startswith='city_'
async def city_kb(call: CallbackQuery, bot: Bot):
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


# startswith='menu_'
async def call_city(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(message_id=call.message.message_id)
    await call.answer()
    action = call.data.split('menu_')[1]
    if action == 'change':
        cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
        city = cur.fetchone()[0][:-2].split(', ')
        await bot.send_message(chat_id=call.from_user.id,
                               text=f'Ваши регионы:',
                               reply_markup=get_button_with_city(city))
    elif action == 'add':
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=f'Отправь свой населенный пункт')
        await state.set_state(StateSet.city)
    elif action == 'my_city':
        await my_city(call, bot=bot)
    elif action == 'alerts':
        cmd = f'SELECT * FROM alerts_base WHERE id = {call.from_user.id}'
        cur.execute(cmd)
        if not(cur.fetchone() is None):
            await call.message.edit_text(text="Меню рассылки:\n\r<strong>Вы подписаны</strong> \U00002705",
                                         reply_markup=menu_of_alerts(),
                                         parse_mode='HTML')
        elif cur.fetchone() is None:
            await call.message.edit_text(text="Меню рассылки:\n\r<strong>Вы не подписаны</strong> \U0000274C",
                                         reply_markup=menu_of_alerts(),
                                         parse_mode='HTML')


# startswith='kb_'), state=_State.city
async def kb_set(call, state: FSMContext, bot: Bot):
    await call.answer()
    action = call.data.split('kb_')[1]
    data = await state.get_data()
    city = data.get('city')
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
    await state.clear()


# startswith='alerts_'
async def call_alerts(call: CallbackQuery, state: FSMContext):
    await state.update_data(call=call)
    await call.answer()
    action = call.data.split('alerts_')[1]
    if action == 'unsubscribe':
        cur.execute(f'DELETE FROM alerts_base WHERE id={call.from_user.id}')
        con.commit()
        await call.message.edit_text(text='Удалил вас из рассылки', reply_markup=menu())
    elif action == 'subscribe':
        await call.message.edit_text(text=f'Отправь регион для рассылки')
        await state.set_state(StateAlerts.subscribe)
    elif action == 'cancel':
        await call.message.edit_text(
            text='Главное меню',
            reply_markup=menu()
        )
