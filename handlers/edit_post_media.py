import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext as FSM
from aiogram.types import CallbackQuery as CQ
from aiogram.types import Message as Mes

from db.queries.post_qs import save_new_post_data
from filters.filters import IsAdmin
from keyboards.admin_kbs import post_kb
from keyboards.main_kbs import cancel_btn
from middlewares.mediagrp import AlbumMiddleware
from utils.format_texts import format_post_text
from utils.misc import delete_prev_message, send_post
from utils.states import PostStates

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())
router.message.middleware(AlbumMiddleware())


@router.callback_query(F.data.startswith("editpostmsg_"))
async def edit_post_message(c: CQ, state: FSM):
    await state.clear()
    post_id = int(c.data.split("_")[-1])

    try:
        await c.message.delete()
    except:
        await c.answer()

    msg = await c.message.answer(
        "💬 Пришлите измененный пост, который хотите запланировать",
        reply_markup=cancel_btn)
    await state.set_state(PostStates.edit_post_message)
    await state.update_data(msg_id=msg.message_id, post_id=post_id)


@router.message(StateFilter(PostStates.edit_post_message), F.text)
async def save_new_post_message_text(m: Mes, state: FSM, bot: Bot, ssn):
    text = m.html_text
    media_kind = "text"
    media_id = "no_media"
    media = []

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))
    await state.clear()

    post_id = data.get("post_id")
    res = await save_new_post_data(
        ssn, post_id, text, media_kind, media_id, media)
    logging.info(f"Admin {m.from_user.id} updated post {post_id} message")

    await send_post(res[0], res[1], bot, m.from_user.id)
    txt = format_post_text(res[0], res[2])
    await m.answer(txt, reply_markup=post_kb(post_id))


@router.message(
    StateFilter(PostStates.edit_post_message), F.media_group_id != None, F.photo
)
@router.message(
    StateFilter(PostStates.edit_post_message), F.media_group_id != None, F.video
)
async def save_new_post_message_media_multi(
        m: Mes, state: FSM, bot: Bot, album: list[Mes], captions, ssn):
    text = captions
    media_kind = "media_group"
    media_id = "media_group"
    media = album

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))
    await state.clear()

    post_id = data.get("post_id")
    res = await save_new_post_data(
        ssn, post_id, text, media_kind, media_id, media)
    logging.info(f"Admin {m.from_user.id} updated post {post_id} message")

    await send_post(res[0], res[1], bot, m.from_user.id)
    txt = format_post_text(res[0], res[2])
    await m.answer(txt, reply_markup=post_kb(post_id))


@router.message(
    StateFilter(PostStates.edit_post_message), F.photo
)
async def save_new_post_message_image(m: Mes, state: FSM, bot: Bot, ssn):
    text = m.html_text if m.caption else "no_text"
    media_kind = "image"
    media_id = m.photo[-1].file_id
    media = []

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))
    await state.clear()

    post_id = data.get("post_id")
    res = await save_new_post_data(
        ssn, post_id, text, media_kind, media_id, media)
    logging.info(f"Admin {m.from_user.id} updated post {post_id} message")

    await send_post(res[0], res[1], bot, m.from_user.id)
    txt = format_post_text(res[0], res[2])
    await m.answer(txt, reply_markup=post_kb(post_id))


@router.message(
    StateFilter(PostStates.edit_post_message), F.video
)
async def save_new_post_message_video(m: Mes, state: FSM, bot: Bot, ssn):
    text = m.html_text if m.caption else "no_text"
    media_kind = "video"
    media_id = m.video.file_id
    media = []

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))
    await state.clear()

    post_id = data.get("post_id")
    res = await save_new_post_data(
        ssn, post_id, text, media_kind, media_id, media)
    logging.info(f"Admin {m.from_user.id} updated post {post_id} message")

    await send_post(res[0], res[1], bot, m.from_user.id)
    txt = format_post_text(res[0], res[2])
    await m.answer(txt, reply_markup=post_kb(post_id))


@router.message(
    StateFilter(PostStates.edit_post_message), F.audio
)
async def save_new_post_message_audio(m: Mes, state: FSM, bot: Bot, ssn):
    text = m.html_text if m.caption else "no_text"
    media_kind = "audio"
    media_id = m.audio.file_id
    media = []

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))
    await state.clear()

    post_id = data.get("post_id")
    res = await save_new_post_data(
        ssn, post_id, text, media_kind, media_id, media)
    logging.info(f"Admin {m.from_user.id} updated post {post_id} message")

    await send_post(res[0], res[1], bot, m.from_user.id)
    txt = format_post_text(res[0], res[2])
    await m.answer(txt, reply_markup=post_kb(post_id))


@router.message(
    StateFilter(PostStates.edit_post_message), F.voice
)
async def save_new_post_message_voice(m: Mes, state: FSM, bot: Bot, ssn):
    text = m.html_text if m.caption else "no_text"
    media_kind = "voice"
    media_id = m.voice.file_id
    media = []

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))
    await state.clear()

    post_id = data.get("post_id")
    res = await save_new_post_data(
        ssn, post_id, text, media_kind, media_id, media)
    logging.info(f"Admin {m.from_user.id} updated post {post_id} message")

    await send_post(res[0], res[1], bot, m.from_user.id)
    txt = format_post_text(res[0], res[2])
    await m.answer(txt, reply_markup=post_kb(post_id))


@router.message(
    StateFilter(PostStates.edit_post_message), F.video_note
)
async def save_new_post_message_video_note(m: Mes, state: FSM, bot: Bot, ssn):
    text = m.html_text if m.caption else "no_text"
    media_kind = "video_note"
    media_id = m.video_note.file_id
    media = []

    data = await state.get_data()
    msg_id = data.get("msg_id")
    asyncio.create_task(delete_prev_message(bot, m.from_user.id, msg_id))
    await state.clear()

    post_id = data.get("post_id")
    res = await save_new_post_data(
        ssn, post_id, text, media_kind, media_id, media)
    logging.info(f"Admin {m.from_user.id} updated post {post_id} message")

    await send_post(res[0], res[1], bot, m.from_user.id)
    txt = format_post_text(res[0], res[2])
    await m.answer(txt, reply_markup=post_kb(post_id))
