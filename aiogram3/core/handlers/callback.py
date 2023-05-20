from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from core.utils.simple_func import *
from core.keyboards.inline import *
from core.utils.database import *
from core.utils.states import *


@flags.chat_action("typing")
# startswith='weather_'
async def weather_with_button(call: CallbackQuery, bot: Bot):
    await call.answer()
    city = call.data.split('weather_')[1]
    get_weather(city)
    if city == 'cancel':
        await bot.delete_message(message_id=call.message.message_id,
                                 chat_id=call.message.chat.id)
    elif city == 'all':
        await get_weather_for_cities(
            user_id=call.from_user.id,
            bot=bot,
            chat_id=call.from_user.id
        )
    else:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=get_weather(city),
                               parse_mode='HTML')


@flags.chat_action("typing")
# startswith='city_'
async def city_kb(call: CallbackQuery, bot: Bot):
    await call.answer()
    city = call.data.split('city_')[1]
    if city == 'cancel':
        await bot.delete_message(message_id=call.message.message_id,
                                 chat_id=call.from_user.id)
    else:
        with create_session() as db:
            cities = db.query(User.city).where(User.id == int(call.from_user.id)).first()[0].replace(city + ', ', '')
            db.query(User).where(User.id == int(call.from_user.id)).update(
                {User.city: cities}
            )
            cities = cities.split(', ')
            await bot.edit_message_text(message_id=call.message.message_id,
                                        chat_id=call.from_user.id,
                                        text=f'Вы удалили регион {city}\n'
                                             f'Какой еще регион хотите удалить?',
                                        reply_markup=get_button_with_city(cities))
            db.commit()


@flags.chat_action("typing")
# startswith='menu_'
async def call_city(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(message_id=call.message.message_id)
    await call.answer()
    action = call.data.split('menu_')[1]
    with create_session() as db:
        if action == 'change':
            city = db.query(User.city).where(User.id == int(call.from_user.id)).first()[0].split(', ')
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
            if db.query(Alert).where(Alert.id == call.from_user.id).first():
                await call.message.edit_text(text="Меню рассылки:\n\r<strong>Вы подписаны</strong> \U00002705",                                             reply_markup=menu_of_alerts(),
                                             parse_mode='HTML')
            elif db.query(Alert).where(Alert.id == call.from_user.id).first() is None:
                await call.message.edit_text(text="Меню рассылки:\n\r<strong>Вы не подписаны</strong> \U0000274C",
                                             reply_markup=menu_of_alerts(),
                                             parse_mode='HTML')


@flags.chat_action("typing")
# startswith='kb_'), state=_State.city
async def kb_set(call, state: FSMContext, bot: Bot):
    await call.answer()
    action = call.data.split('kb_')[1]
    data = await state.get_data()
    city = data.get('city') + ', '
    with create_session() as db:
        if action == 'add':
            cities = db.query(User.city).where(User.id == int(call.from_user.id)).first()[0]
            if city in cities:
                await bot.edit_message_text(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    text=f'Этот город уже есть в списке'
                )
            else:
                cities = f'{cities}{city}'
                db.query(User).where(User.id == int(call.from_user.id)).update({
                    User.city: cities, User.active: True
                })
                await bot.edit_message_text(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    text=f'Город добавлен'
                )
            db.commit()
        elif action == 'set':
            db.query(User).where(User.id == int(call.from_user.id)).update({
                    User.city: city, User.active: True
                })
            await bot.edit_message_text(chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        text=f'Город установлен!\nВаш регион: {city[:-2:]}')
        db.commit()
        await state.clear()


@flags.chat_action("typing")
# startswith='alerts_'
async def call_alerts(call: CallbackQuery, state: FSMContext):
    await state.update_data(call=call)
    await call.answer()
    action = call.data.split('alerts_')[1]
    if action == 'unsubscribe':
        with create_session() as db:
            db.query(Alert).where(Alert.id == int(call.from_user.id)).delete()
            db.commit()
        await call.message.edit_text(text='Удалил вас из рассылки', reply_markup=menu())
    elif action == 'subscribe':
        await call.message.edit_text(text=f'Отправь регион для рассылки')
        await state.set_state(StateAlerts.subscribe)
    elif action == 'cancel':
        await call.message.edit_text(
            text='Главное меню',
            reply_markup=menu()
        )
