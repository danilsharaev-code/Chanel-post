from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    send_all = State()
    send_to = State()


class PostStates(StatesGroup):
    post_message = State()
    post_time = State()
    post_channels = State()
    post_confirm = State()

    edit_post_message = State()
    edit_post_time = State()
    edit_post_channels = State()
