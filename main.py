import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from back_handler import transition, StateManager
from state import TestState

logging.basicConfig(level=logging.INFO)

bot = Bot(token="7225955525:AAGF91ehq5tS5HklS8oinAInxLYTWc8fgB0")
dp = Dispatcher()

router = Router()


def generateKeyboard(buttons_list: list[list]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for buttons_row in buttons_list:
        builder.row(*[KeyboardButton(text=button) for button in buttons_row])

    return builder.as_markup(resize_keyboard=True)


@router.message(StateFilter(None), Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(TestState.state_init)

    await message.answer("Hello!", reply_markup=generateKeyboard([[
        'Кнопка 1'
    ]]))


@transition(from_state=TestState.state_second, action=cmd_start)
@router.message(TestState.state_init, F.text == 'Кнопка 1')
async def button1(message: types.Message, state: FSMContext):
    await state.set_state(TestState.state_second)
    await message.answer("Кнопка 1", reply_markup=generateKeyboard([[
        'Кнопка 2'
    ], [
        'Назад'
    ]]))


@transition(from_state=TestState.finish, action=button1)
@router.message(TestState.state_second, F.text == 'Кнопка 2')
async def button2(message: types.Message, state: FSMContext):
    await state.set_state(TestState.finish)
    await message.answer("Кнопка 2", reply_markup=generateKeyboard([[
        'Назад'
    ]]))


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    StateManager.init(router=router)
    asyncio.run(main())
