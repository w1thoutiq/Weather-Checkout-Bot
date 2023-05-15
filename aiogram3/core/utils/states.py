from aiogram.fsm.state import StatesGroup, State


class StateSet(StatesGroup):
    city = State()


class StateAlerts(StatesGroup):
    subscribe = State()