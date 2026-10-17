
import calendar

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (ChatAdministratorRights, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton,
                           KeyboardButtonRequestChat, ReplyKeyboardMarkup)

from db.models import Channel, ChannelPost
from keyboards.cb_data import CalendarCB
from utils.const import month_names


def user_channels_kb(channels):
    btns = []
    channel: Channel
    for channel in channels:
        btns.append([InlineKeyboardButton(text=channel.title,
                    callback_data=f"viewchannel_{channel.id}")])

    return InlineKeyboardMarkup(inline_keyboard=btns)


def channel_posts_kb(ch_id, posts):
    btns = []
    if len(posts) > 0:
        ch_post: ChannelPost
        for ch_post in posts:
            btns.append([InlineKeyboardButton(text=ch_post.date_str,
                        callback_data=f"viewpost_{ch_post.id}")])
    btns.append([InlineKeyboardButton(text="🗑️ Удалить канал",
                callback_data=f"deletechannel_{ch_id}")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def post_kb(post_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить пост",
                                     callback_data=f"editpostmsg_{post_id}")
            ],
            [
                InlineKeyboardButton(text="Изменить время публикации",
                                     callback_data=f"editposttime_{post_id}")
            ],
            [
                InlineKeyboardButton(text="Изменить каналы публикации",
                                     callback_data=f"editpostchannels_{post_id}")
            ],
            [
                InlineKeyboardButton(text="🗑️ Удалить пост",
                                     callback_data=f"deletepost_{post_id}")
            ],
        ]
    )
    return keyboard


def posts_kb(posts):
    btns = []
    ch_post: ChannelPost
    for ch_post in posts:
        btns.append([InlineKeyboardButton(text=ch_post.date_str,
                    callback_data=f"viewpost_{ch_post.id}")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def post_calendar_kb(year, month, cur_month=False, today=99):
    btns = []

    prev_month = (month - 1) or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month % 12 + 1
    next_year = year + 1 if month == 12 else year

    year_prev = year - 1
    year_next = year + 1
    year_btns = [
        InlineKeyboardButton(text=f"« {year_prev}", callback_data=CalendarCB(
            action="prev", year=year_prev, month=month, day=0).pack()),
        InlineKeyboardButton(text=f"{year_next} »", callback_data=CalendarCB(
            action="next", year=year_next, month=month, day=0).pack())
    ]
    btns.append(year_btns)

    header_btns = [
        InlineKeyboardButton(
            text="«", callback_data=CalendarCB(
                action="prev", year=prev_year, month=prev_month, day=0).pack()),
        InlineKeyboardButton(
            text=f"{month_names.get(str(month))} {year}",
            callback_data="useless"),
        InlineKeyboardButton(
            text="»", callback_data=CalendarCB(
                action="next", year=next_year, month=next_month, day=0).pack())
    ]
    btns.append(header_btns)

    weekdays_btns = []
    for d in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        weekdays_btns.append(
            InlineKeyboardButton(text=d, callback_data="useless"))
    btns.append(weekdays_btns)

    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(
                    text=" ", callback_data="useless"))
            else:
                if cur_month and (today == day):
                    str_day = f"•{day}"
                else:
                    str_day = str(day)
                row.append(InlineKeyboardButton(
                    text=str_day, callback_data=CalendarCB(
                        action="day", year=year, month=month, day=day).pack()))
        btns.append(row)

    btns.append([InlineKeyboardButton(
        text="Отменить", callback_data="cancel_cb")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def post_hours_kb(hour, is_today, date_str):
    btns = [
        [
            InlineKeyboardButton(
                text=f"Дата: {date_str}", callback_data="useless")
        ],
        [
            InlineKeyboardButton(
                text="———— Выберите час ————", callback_data="useless")
        ],
    ]
    line_btns = []
    for i in range(24):
        if is_today:
            if i < hour:
                line_btns.append(InlineKeyboardButton(
                    text="•", callback_data="useless"))
            else:
                if len(str(i)) == 1:
                    hour_str = f"0{i}"
                else:
                    hour_str = str(i)
                line_btns.append(InlineKeyboardButton(
                    text=hour_str, callback_data=f"posthour_{hour_str}"))
        else:
            if len(str(i)) == 1:
                hour_str = f"0{i}"
            else:
                hour_str = str(i)
            line_btns.append(InlineKeyboardButton(
                text=hour_str, callback_data=f"posthour_{hour_str}"))
        if len(line_btns) == 6:
            btns.append(line_btns)
            line_btns = []
    if len(line_btns) > 0:
        btns.append(line_btns)

    btns.append([InlineKeyboardButton(
        text="↩️ Назад", callback_data="backtoposttime")])
    btns.append([InlineKeyboardButton(
        text="Отменить", callback_data="cancel_cb")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def post_minutes_kb(date_str, hour_str):
    btns = [
        [
            InlineKeyboardButton(
                text=f"Дата: {date_str}", callback_data="useless")
        ],
        [
            InlineKeyboardButton(
                text=f"Часы: {hour_str}", callback_data="useless")
        ],
        [
            InlineKeyboardButton(
                text="———— Выберите минуты ————", callback_data="useless")
        ],
        [
            InlineKeyboardButton(
                text="00", callback_data="postminute_00"),
            InlineKeyboardButton(
                text="05", callback_data="postminute_05"),
            InlineKeyboardButton(
                text="10", callback_data="postminute_10"),
            InlineKeyboardButton(
                text="15", callback_data="postminute_15"),
            InlineKeyboardButton(
                text="20", callback_data="postminute_20"),
            InlineKeyboardButton(
                text="25", callback_data="postminute_25"),
        ],
        [
            InlineKeyboardButton(
                text="30", callback_data="postminute_30"),
            InlineKeyboardButton(
                text="35", callback_data="postminute_35"),
            InlineKeyboardButton(
                text="40", callback_data="postminute_40"),
            InlineKeyboardButton(
                text="45", callback_data="postminute_45"),
            InlineKeyboardButton(
                text="50", callback_data="postminute_50"),
            InlineKeyboardButton(
                text="55", callback_data="postminute_55"),
        ],

    ]
    btns.append([InlineKeyboardButton(
        text="↩️ Назад", callback_data="backtoposttime")])
    btns.append([InlineKeyboardButton(
        text="Отменить", callback_data="cancel_cb")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def post_channels_kb(selected, channels):
    btns = []
    chnl: Channel
    for chnl in channels:
        if chnl.id in selected:
            icon = "✅"
            cb = "unselectchannel"
        else:
            icon = ""
            cb = "selectchannel"
        btns.append([InlineKeyboardButton(
            text=f"{icon} {chnl.title}",
            callback_data=f"{cb}_{chnl.id}")])
    btns.append([InlineKeyboardButton(
        text="Выбрать все", callback_data="allchannelsselect")])
    btns.append([InlineKeyboardButton(
        text="⏩️ Далее", callback_data="channelsselected")])
    btns.append([InlineKeyboardButton(
        text="Отменить", callback_data="cancel_cb")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


conf_post_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Запланировать пост",
                                 callback_data="confaddpost")
        ],
        [
            InlineKeyboardButton(
                text="Отменить", callback_data="cancel_cb")
        ],
    ]
)
