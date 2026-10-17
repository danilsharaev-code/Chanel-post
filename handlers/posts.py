import datetime
import logging

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext as FSM
from aiogram.types import CallbackQuery as CQ
from aiogram.types import Message as Mes

from db.queries.global_qs import get_channel_ids
from db.queries.post_qs import (delete_post, get_all_posts,
                                get_post_channel_ids, get_post_info,
                                save_new_post_channels, save_new_post_date)
from keyboards.admin_kbs import (post_calendar_kb, post_channels_kb,
                                 post_hours_kb, post_kb, post_minutes_kb,
                                 posts_kb)
from keyboards.cb_data import CalendarCB
from utils.format_texts import format_post_text
from utils.misc import check_input_date, send_post
from utils.states import PostStates

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


@router.message(F.text == "Мои посты")
async def view_all_posts(m: Mes, state: FSM, ssn):
    await state.clear()

    posts = await get_all_posts(ssn)
    if len(posts) == 0:
        await m.answer("Нет запланированных постов")
    else:
        txt = "Список запланированных постов"
        await m.answer(txt, reply_markup=posts_kb(posts))


@router.callback_query(F.data.startswith("viewpost_"))
async def view_post(c: CQ, ssn, state: FSM, bot: Bot):
    await state.clear()

    post_id = int(c.data.split("_")[-1])

    res = await get_post_info(ssn, post_id)
    if res == "error":
        await c.answer("Возникла ошибка!", show_alert=True)
        try:
            await c.message.delete()
        except:
            pass

    else:
        try:
            await c.message.delete()
        except:
            await c.answer()

        await send_post(res[0], res[1], bot, c.from_user.id)

        txt = format_post_text(res[0], res[2])
        await c.message.answer(txt, reply_markup=post_kb(post_id))


@router.callback_query(F.data.startswith("deletepost_"))
async def post_deleted_by_admin(c: CQ, ssn, state: FSM):
    await state.clear()

    post_id = int(c.data.split("_")[-1])

    await delete_post(ssn, post_id)
    logging.info(f"Admin {c.from_user.id} deleted post {post_id}")

    await c.answer("✅ Пост удален")
    try:
        await c.message.delete()
    except:
        pass


@router.callback_query(F.data.startswith("editposttime_"))
async def edit_post_time(c: CQ, state: FSM):
    await state.clear()

    post_id = int(c.data.split("_")[-1])

    try:
        await c.message.delete()
    except:
        await c.answer()

    date = datetime.datetime.now()
    await c.message.answer(
        "📆 Укажите новую дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))
    await state.set_state(PostStates.edit_post_time)
    await state.update_data(post_id=post_id)


@router.callback_query(
    StateFilter(PostStates.edit_post_time),
    CalendarCB.filter(F.action.in_({"prev", "next"}))
)
async def paginate_new_post_calendar(c: CQ, callback_data: CalendarCB):
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
    StateFilter(PostStates.edit_post_time), F.data == "backtoposttime"
)
async def back_to_new_post_time(c: CQ, state: FSM):
    date = datetime.datetime.now()

    try:
        await c.message.delete()
    except:
        await c.answer()

    msg = await c.message.answer(
        "📆 Укажите новую дату публикации поста",
        reply_markup=post_calendar_kb(
            date.year, date.month, cur_month=True, today=date.day))
    await state.update_data(msg_id=msg.message_id)


@router.callback_query(
    StateFilter(PostStates.edit_post_time),
    CalendarCB.filter(F.action == "day")
)
async def save_updated_post_date(c: CQ, callback_data: CalendarCB, state: FSM):
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

        txt = "⌚ Укажите новое время публикации поста"
        await c.message.answer(
            txt, reply_markup=post_hours_kb(date.hour, is_today, prev_date_str))
        await state.update_data(
            prev_date_str=prev_date_str, prev_date_digit=prev_date_digit,
            day=day, month=month, year=year)


@router.callback_query(
    StateFilter(PostStates.edit_post_time), F.data.startswith("posthour_")
)
async def save_new_post_hour(c: CQ, state: FSM):
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
    StateFilter(PostStates.edit_post_time), F.data.startswith("postminute_")
)
async def save_new_post_minute(c: CQ, state: FSM, ssn, bot):
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

        try:
            await c.message.delete()
        except:
            await c.answer()
        await state.clear()

        post_id = data.get("post_id")
        res = await save_new_post_date(ssn, post_id, date_str, date_digit)
        logging.info(f"Admin {c.from_user.id} updated post {post_id} time")

        await send_post(res[0], res[1], bot, c.from_user.id)
        txt = format_post_text(res[0], res[2])
        await c.message.answer(txt, reply_markup=post_kb(post_id))


@router.callback_query(F.data.startswith("editpostchannels_"))
async def edit_post_channels(c: CQ, state: FSM, ssn):
    await state.clear()

    post_id = int(c.data.split("_")[-1])

    try:
        await c.message.delete()
    except:
        await c.answer()

    res = await get_post_channel_ids(ssn, post_id)
    txt = "Выберите каналы для публикации поста"
    await c.message.answer(
        txt, reply_markup=post_channels_kb(res[0], res[1]))
    await state.set_state(PostStates.edit_post_channels)
    await state.update_data(selected=res[0], channels=res[1], post_id=post_id)


@router.callback_query(
    StateFilter(PostStates.edit_post_channels), F.data.startswith(
        "selectchannel_")
)
async def select_new_post_channel(c: CQ, state: FSM):
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
    StateFilter(PostStates.edit_post_channels), F.data.startswith(
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
    StateFilter(PostStates.edit_post_channels), F.data == "allchannelsselect"
)
async def post_new_all_channels_select(c: CQ, state: FSM, bot: Bot, ssn):
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
    StateFilter(PostStates.edit_post_channels), F.data == "channelsselected"
)
async def post_new_channels_selected(c: CQ, state: FSM, bot: Bot, ssn):
    data = await state.get_data()
    selected: list = data.get("selected")
    if len(selected) == 0:
        await c.answer("⚠️ Возникла ошибка! Необходимо выбрать минимум один канал")
    else:
        try:
            await c.message.delete()
        except:
            await c.answer()

        await state.clear()

        post_id = data.get("post_id")
        res = await save_new_post_channels(ssn, post_id, selected)
        logging.info(f"Admin {c.from_user.id} updated post {post_id} channels")

        await send_post(res[0], res[1], bot, c.from_user.id)
        txt = format_post_text(res[0], res[2])
        await c.message.answer(txt, reply_markup=post_kb(post_id))
