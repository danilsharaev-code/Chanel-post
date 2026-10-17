import asyncio
import datetime
import logging

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext as FSM
from aiogram.types import CallbackQuery as CQ
from aiogram.types import Message as Mes

from db.queries.global_qs import get_channel_ids, get_channels
from db.queries.post_qs import get_channels_by_ids, new_post
from filters.filters import IsAdmin
from keyboards.admin_kbs import (conf_post_kb, post_calendar_kb,
                                 post_channels_kb, post_hours_kb,
                                 post_minutes_kb)
from keyboards.cb_data import CalendarCB
from keyboards.main_kbs import cancel_btn, main_kb
from middlewares.mediagrp import AlbumMiddleware
from utils.format_texts import format_pre_created_post_text
from utils.misc import (check_input_date, delete_prev_message,
                        send_pre_created_post)
from utils.states import PostStates

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())
router.message.middleware(AlbumMiddleware())


@router.message(F.text == "Создать пост")
async def start_add_post(m: Mes, state: FSM):
    await state.clear()

    msg = await m.answer(
        "💬 Пришлите пост, который хотите запланировать",
        reply_markup=cancel_btn)
    await state.set_state(PostStates.post_message)
    await state.update_data(msg_id=msg.message_id)


@router.message(StateFilter(PostStates.post_message), F.text)
async def save_post_message_text(m: Mes, state: FSM, bot: Bot):
    text = m.html_text
    media_kind = "text"
    media_id = "no_media"

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))

    date = datetime.datetime.now()
    msg = await m.answer(
        "📆 Укажите дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))

    await state.set_state(PostStates.post_time)
    await state.update_data(
        msg_id=msg.message_id, text=text,
        media_kind=media_kind, media_id=media_id, media=[])


@router.message(
    StateFilter(PostStates.post_message), F.media_group_id != None, F.photo
)
@router.message(
    StateFilter(PostStates.post_message), F.media_group_id != None, F.video
)
async def save_post_message_media_multi(
        m: Mes, state: FSM, bot: Bot, album: list[Mes], captions):
    text = captions
    media_kind = "media_group"
    media_id = "media_group"

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))

    date = datetime.datetime.now()
    msg = await m.answer(
        "📆 Укажите дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))

    await state.set_state(PostStates.post_time)
    await state.update_data(
        msg_id=msg.message_id, text=text,
        media_kind=media_kind, media_id=media_id, media=album)


@router.message(
    StateFilter(PostStates.post_message), F.photo
)
async def save_post_message_image(m: Mes, state: FSM, bot: Bot):
    text = m.html_text if m.caption else "no_text"
    media_kind = "image"
    media_id = m.photo[-1].file_id

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))

    date = datetime.datetime.now()
    msg = await m.answer(
        "📆 Укажите дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))

    await state.set_state(PostStates.post_time)
    await state.update_data(
        msg_id=msg.message_id, text=text,
        media_kind=media_kind, media_id=media_id, media=[])


@router.message(
    StateFilter(PostStates.post_message), F.video
)
async def save_post_message_video(m: Mes, state: FSM, bot: Bot):
    text = m.html_text if m.caption else "no_text"
    media_kind = "video"
    media_id = m.video.file_id

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))

    date = datetime.datetime.now()
    msg = await m.answer(
        "📆 Укажите дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))

    await state.set_state(PostStates.post_time)
    await state.update_data(
        msg_id=msg.message_id, text=text,
        media_kind=media_kind, media_id=media_id, media=[])


@router.message(
    StateFilter(PostStates.post_message), F.audio
)
async def save_post_message_audio(m: Mes, state: FSM, bot: Bot):
    text = m.html_text if m.caption else "no_text"
    media_kind = "audio"
    media_id = m.audio.file_id

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))

    date = datetime.datetime.now()
    msg = await m.answer(
        "📆 Укажите дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))

    await state.set_state(PostStates.post_time)
    await state.update_data(
        msg_id=msg.message_id, text=text,
        media_kind=media_kind, media_id=media_id, media=[])


@router.message(
    StateFilter(PostStates.post_message), F.voice
)
async def save_post_message_voice(m: Mes, state: FSM, bot: Bot):
    text = m.html_text if m.caption else "no_text"
    media_kind = "voice"
    media_id = m.voice.file_id

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))

    date = datetime.datetime.now()
    msg = await m.answer(
        "📆 Укажите дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))

    await state.set_state(PostStates.post_time)
    await state.update_data(
        msg_id=msg.message_id, text=text,
        media_kind=media_kind, media_id=media_id, media=[])


@router.message(
    StateFilter(PostStates.post_message), F.video_note
)
async def save_post_message_video_note(m: Mes, state: FSM, bot: Bot):
    text = m.html_text if m.caption else "no_text"
    media_kind = "video_note"
    media_id = m.video_note.file_id

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))

    date = datetime.datetime.now()
    msg = await m.answer(
        "📆 Укажите дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))

    await state.set_state(PostStates.post_time)
    await state.update_data(
        msg_id=msg.message_id, text=text,
        media_kind=media_kind, media_id=media_id, media=[])


@router.callback_query(
    StateFilter(PostStates.post_time),
    CalendarCB.filter(F.action.in_({"prev", "next"}))
)
async def paginate_post_calendar(c: CQ, callback_data: CalendarCB):
    year = callback_data.year
    month = callback_data.month

    date = datetime.datetime.now()
    curr_month = (month == date.month) and (year == date.year)
    try:
        await c.message.edit_reply_markup(reply_markup=post_calendar_kb(
            year, month, cur_month=curr_month, today=date.day))
    except:
        await c.answer()


@router.callback_query(
    StateFilter(PostStates.post_time), F.data == "backtoposttime"
)
async def back_to_post_time(c: CQ, state: FSM):
    date = datetime.datetime.now()

    try:
        await c.message.delete()
    except:
        await c.answer()

    msg = await c.message.answer(
        "📆 Укажите дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))
    await state.update_data(msg_id=msg.message_id)


@router.callback_query(
    StateFilter(PostStates.post_time),
    CalendarCB.filter(F.action == "day")
)
async def save_post_date(c: CQ, callback_data: CalendarCB, state: FSM):
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day

    date = datetime.datetime.now()
    check = check_input_date(f"{day}.{month}.{year} 23:59")
    if check == "error":
        await c.answer("⚠️ Возникла ошибка! Нельзя выбрать прошедшую дату")
    else:
        prev_date_str = check[1]
        prev_date_digit = check[2]
        if (day == date.day) and (month == date.month) and (year == date.year):
            is_today = True
        else:
            is_today = False

        try:
            await c.message.delete()
        except:
            await c.answer()

        txt = "⌚ Укажите время публикации поста"
        await c.message.answer(
            txt, reply_markup=post_hours_kb(date.hour, is_today, prev_date_str))
        await state.update_data(
            prev_date_str=prev_date_str, prev_date_digit=prev_date_digit,
            day=day, month=month, year=year)


@router.callback_query(
    StateFilter(PostStates.post_time), F.data.startswith("posthour_")
)
async def save_post_hour(c: CQ, state: FSM):
    hour_str = c.data.split("_")[-1]
    data = await state.get_data()
    prev_date_str = data.get("prev_date_str")
    txt = "⌚ Укажите время публикации поста"

    try:
        await c.message.delete()
    except:
        await c.answer()

    await c.message.answer(
        txt, reply_markup=post_minutes_kb(prev_date_str, hour_str))
    await state.update_data(hour_str=hour_str)


@router.callback_query(
    StateFilter(PostStates.post_time), F.data.startswith("postminute_")
)
async def save_post_minute(c: CQ, state: FSM, ssn):
    minutes_str = c.data.split("_")[-1]
    data = await state.get_data()
    prev_date_str = data.get("prev_date_str")
    prev_date_digit = data.get("prev_date_digit")

    hour_str = data.get("hour_str")
    check = check_input_date(
        f"{data['day']}.{data['month']}.{data['year']} {hour_str}:{minutes_str}")
    if check == "error":
        await c.answer("⚠️ Возникла ошибка! Нельзя выбрать прошедшую дату")
    else:
        date_str = f"{prev_date_str} {hour_str}:{minutes_str}"
        date_digit = f"{prev_date_digit} {hour_str}:{minutes_str}"

        data["date_str"] = date_str
        data["date_digit"] = date_digit

        try:
            await c.message.delete()
        except:
            await c.answer()

        channels = await get_channels(ssn)
        txt = "Выберите каналы для публикации поста"
        await c.message.answer(txt, reply_markup=post_channels_kb([], channels))

        await state.set_state(PostStates.post_channels)
        await state.update_data(
            date_str=date_str, date_digit=date_digit,
            selected=[], channels=channels)


@router.callback_query(
    StateFilter(PostStates.post_channels), F.data.startswith("selectchannel_")
)
async def select_post_channel(c: CQ, state: FSM):
    ch_id = int(c.data.split("_")[-1])

    data = await state.get_data()
    selected = data.get("selected")
    channels = data.get("channels")

    if ch_id not in selected:
        selected.append(ch_id)

    try:
        await c.message.edit_reply_markup(
            reply_markup=post_channels_kb(selected, channels))
    except:
        await c.answer()

    await state.update_data(selected=selected)


@router.callback_query(
    StateFilter(PostStates.post_channels), F.data.startswith(
        "unselectchannel_")
)
async def unselect_post_channel(c: CQ, state: FSM):
    ch_id = int(c.data.split("_")[-1])

    data = await state.get_data()
    selected: list = data.get("selected")
    channels = data.get("channels")

    if ch_id in selected:
        try:
            selected.remove(ch_id)
        except:
            pass

    try:
        await c.message.edit_reply_markup(
            reply_markup=post_channels_kb(selected, channels))
    except:
        await c.answer()

    await state.update_data(selected=selected)


@router.callback_query(
    StateFilter(PostStates.post_channels), F.data == "allchannelsselect"
)
async def post_all_channels_select(c: CQ, state: FSM, bot: Bot, ssn):
    data = await state.get_data()
    selected = list(await get_channel_ids(ssn))
    channels = data.get("channels")

    try:
        await c.message.edit_reply_markup(
            reply_markup=post_channels_kb(selected, channels))
    except:
        await c.answer()

    await state.update_data(selected=selected)


@router.callback_query(
    StateFilter(PostStates.post_channels), F.data == "channelsselected"
)
async def post_channels_selected(c: CQ, state: FSM, bot: Bot, ssn):
    data = await state.get_data()
    selected: list = data.get("selected")
    if len(selected) == 0:
        await c.answer("⚠️ Возникла ошибка! Необходимо выбрать минимум один канал")
    else:
        try:
            await c.message.delete()
        except:
            await c.answer()

        await send_pre_created_post(
            data['text'], data['media_kind'], data['media_id'],
            data['media'], bot, c.from_user.id)
        channels = await get_channels_by_ids(ssn, data['selected'])
        txt = format_pre_created_post_text(data['date_str'], channels)
        await c.message.answer(txt, reply_markup=conf_post_kb)
        await state.set_state(PostStates.post_confirm)


@router.callback_query(
    StateFilter(PostStates.post_confirm), F.data == "confaddpost"
)
async def post_channels_confirmed(c: CQ, state: FSM, bot: Bot, ssn):
    data = await state.get_data()
    await state.clear()

    await new_post(ssn, data)
    logging.info(f"Admin {c.from_user.id} added new post")
    try:
        await c.message.delete()
    except:
        await c.answer()
    await c.message.answer("✅ Пост добавлен", reply_markup=main_kb)
