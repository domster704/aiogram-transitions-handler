from aiogram.fsm.state import StatesGroup, State


class TestState(StatesGroup):
    state_init = State()
    state_second = State()
    finish = State()
