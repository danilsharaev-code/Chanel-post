from aiogram.filters.callback_data import CallbackData


class PageCB(CallbackData, prefix="page"):
    num: int
    last: int


class CalendarCB(CallbackData, prefix="clndr"):
    action: str
    year: int
    month: int
    day: int
