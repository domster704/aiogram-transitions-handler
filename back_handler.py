from __future__ import annotations

from typing import Callable, Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message


class Singleton(type):
    """
    Метакласс для Singleton
    """

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)

            return cls.__instance
        else:
            return cls.__instance


class StateTransition(object):
    """
    Class describes data about transition between states
    """
    def __init__(self,
                 *,
                 from_state: State,
                 to_state: Optional[State] = None,
                 transition_action: Callable
                 ):
        self.state_first: State = from_state
        self.state_backing: Optional[State] = to_state
        self.transition_action: Callable = transition_action

    def getUniqueKey(self) -> str:
        return f"{self.state_first.state}"

    def __repr__(self) -> str:
        return f"{self.transition_action}: {self.state_first.state} -> {self.state_backing}"


class StateManager(metaclass=Singleton):
    """
    Class-manager of transitions between states
    """
    TRANSITIONS_BUTTONS_DEFAULT_TEXT = {'Назад', 'Back', 'Cancel'}

    def __init__(self):
        self.transitions: list[StateTransition] = []

    def add_transition(self,
                       from_state: State,
                       to_state: Optional[State],
                       transition_action: Callable
                       ) -> None:
        for backData in self.transitions:
            if backData.getUniqueKey() == f'{from_state.state}':
                raise Exception("The state_first has already been added")

        self.transitions.append(StateTransition(from_state=from_state,
                                                to_state=to_state,
                                                transition_action=transition_action))

    @staticmethod
    def init(*,
             router: Router,
             transition_buttons_text=None
             ) -> None:
        """
        Необходимо вызвать перед Dispatcher().start_polling(Bot(token="..."))
        :param router:
        :param transition_buttons_text:
        :return:
        """
        if transition_buttons_text is None:
            transition_buttons_text = StateManager.TRANSITIONS_BUTTONS_DEFAULT_TEXT

        @router.message(F.text.in_(transition_buttons_text))
        async def back_handler(message: Message, state: FSMContext):
            backHandler = StateManager()

            current_state = await state.get_state()

            for backData in backHandler.transitions:
                if backData.state_first.state == current_state:
                    if backData.state_backing is not None:
                        await state.set_state(backData.state_backing)

                    await backData.transition_action(message, state)
                    break


def transition(*,
               from_state: State,
               action: Callable,
               to_state: Optional[State] = None,
               ) -> Callable:
    """
    Декоратор для добавления возможности переходить в другие состояния. Для этого необходимо реализовать кнопку (по
    умолчанию с текстом {StateManager.TRANSITIONS_BUTTONS_DEFAULT_TEXT})
    :param from_state: Состояние из которого будет нажиматься кнопка.
    :param to_state: Состояние, в которое надо перейти при нажатии на кнопку.
    :param action: Функция, вызываемая при нажатии на кнопку
    :return: Декорируемая функция
    """
    if from_state is None or action is None:
        raise TypeError("Arguments state_first and backing_to_func must not be None")

    backHandler = StateManager()
    backHandler.add_transition(
        from_state,
        to_state,
        action
    )

    def decorator(func: Callable):
        async def wrapper(*arg, **kwargs):
            await func(*arg, **kwargs)

        return wrapper

    return decorator
