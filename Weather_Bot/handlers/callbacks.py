# import sys
# import os
# from aiogram.dispatcher.filters import Text
# from aiogram import Bot, Dispatcher
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher import FSMContext
# from aiogram.types import CallbackQuery
#
# # sys.path.append(os.path.dirname(os.getcwd()))
# from Keyboards import *
# from database import *
# from handlers.message import *
#
# class _State(StatesGroup):
#     city = State()
#
# bot = Bot(
#     token='6178245829:AAGwMAb-dPju3eSoNRBT8n3pxRPoFISuMLA')
# dp = Dispatcher(bot, storage=MemoryStorage())
#
#
# @dp.callback_query_handler(Text(startswith='menu_'))
# async def call_city(call: CallbackQuery):
#     await call.answer()
#     action = call.data.split('menu_')[1]
#     if action == 'change':
#         cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
#         city = cur.fetchone()[0][:-2].split(', ')
#         await bot.send_message(chat_id=call.from_user.id,
#                                text=f'Ваши регионы:',
#                                reply_markup=get_button_with_city(city))
#     elif action == 'add':
#         await first_set_city(call)
#     else:
#         await my_city(call)
#
#
# @dp.callback_query_handler(Text(startswith='weather_'))
# async def weather_with_button(call:CallbackQuery):
#     await call.answer()
#     city = call.data.split('weather_')[1]
#     await get_weather(city)
#     if city == 'cancel':
#         await bot.delete_message(message_id=call.message.message_id,
#                                  chat_id=call.from_user.id)
#     elif city == 'all':
#         await get_weather_for_cities(call.from_user.id)
#     else:
#         await bot.send_message(chat_id=call.from_user.id,
#                                text=await get_weather(city),
#                                parse_mode='HTML')
#
#
# @dp.callback_query_handler(Text(startswith='city_'))
# async def city_kb(call: CallbackQuery):
#     await call.answer()
#     city = call.data.split('city_')[1]
#     if city == 'cancel':
#         await bot.delete_message(message_id=call.message.message_id,
#                                     chat_id=call.from_user.id)
#     else:
#         cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
#         cities = cur.fetchone()[0].replace(city + ', ' , '')
#         cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)",
#                     (call.from_user.username, call.from_user.id, cities, 1,))
#         con.commit()
#         cities = cities.split(', ')
#         await bot.edit_message_text(message_id=call.message.message_id,
#                                     chat_id=call.from_user.id,
#                                     text=f'Вы удалили регион {city}:\n'
#                                          f'Какой еще регион хотите удалить?',
#                                     reply_markup=get_button_with_city(cities))
#
#
# @dp.callback_query_handler(text='help')  # Обработка callback из кнопки help в сообщении /start
# async def help_in_welcome(call: CallbackQuery):
#     await call.answer()
#     await send_help(call)
#
#
# @dp.callback_query_handler(Text(startswith='kb_'), state=_State.city)
# async def kb_set(call, state: FSMContext):
#     await call.answer()
#     action = call.data.split('kb_')[1]
#     async with state.proxy() as data:
#         city = data['city']
#     if action == 'add':
#         cur.execute(f"SELECT city FROM base WHERE id={call.from_user.id}")
#         cities = cur.fetchone()[0] + city + ', '
#         cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)",
#                     (call.from_user.username, call.from_user.id, cities, 1,))
#         con.commit()
#         await bot.edit_message_text(chat_id=call.from_user.id,
#                                     message_id=call.message.message_id,
#                                     text=f'Город добавлен')
#     elif action == 'set':
#         cur.execute(f"REPLACE INTO base (username, id, city, active) VALUES (?,?,?,?)", (
#             call.from_user.username, call.from_user.id, city+', ', 1,))
#         con.commit()
#         await bot.edit_message_text(chat_id=call.from_user.id,
#                                     message_id=call.message.message_id,
#                                text=f'Город установлен!\nВаш регион: {city}\n')
#     await state.finish()
