from aiogram.fsm.state import State, StatesGroup

class BotCreationStates(StatesGroup):
    waiting_token = State()
    interview = State()
    confirmation = State()