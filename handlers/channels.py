import logging

from aiogram import Bot, F, Router
from aiogram.filters import LEAVE_TRANSITION, ChatMemberUpdatedFilter
from aiogram.fsm.context import FSMContext as FSM
from aiogram.types import CallbackQuery as CQ
from aiogram.types import ChatMemberUpdated
from aiogram.types import Message as Mes

from db.models import Channel
from db.queries.global_qs import (channel_deleted, get_channel, get_channels,
                                  new_channel)
from filters.filters import IsAdmin
from keyboards.admin_kbs import channel_posts_kb, user_channels_kb

router = Router()


@router.message(F.chat_shared, F.chat.type == "private", IsAdmin())
async def channel_added_by_admin(m: Mes, ssn, bot: Bot):
    chat = m.chat_shared
    channel_id = chat.chat_id
    check_chat = await bot.get_chat(channel_id)
    title = check_chat.title

    await new_channel(ssn, channel_id, title)
    await m.answer(f"✅ Канал <b>{title}</b> добавлен")
    logging.info(f"Admin {m.from_user.id} added channel {channel_id} {title}")


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION),
)
async def bot_kicked(event: ChatMemberUpdated, ssn):
    channel_id = event.chat.id
    res = await channel_deleted(ssn, channel_id, "auto")
    if res != "not_found":
        logging.info(f"Bot deleted from channel {channel_id} {res}")


@router.message(F.text == "Мои каналы", F.chat.type == "private", IsAdmin())
async def my_channels(m: Mes, state: FSM, ssn):
    await state.clear()

    channels = await get_channels(ssn)
    if len(channels) == 0:
        await m.answer("💬 Вы еще не добавили ниодного канала")
    else:
        txt = "💬 Выберите канал из списка"
        await m.answer(txt, reply_markup=user_channels_kb(channels))


@router.callback_query(F.data.startswith("viewchannel_"))
async def view_channel(c: CQ, ssn):
    item_id = int(c.data.split("_")[-1])

    try:
        await c.message.delete()
    except:
        await c.answer()

    res = await get_channel(ssn, item_id)
    channel: Channel = res[0]
    txt = f"Запланированные посты канала <b>{channel.title}</b>"
    await c.message.answer(txt, reply_markup=channel_posts_kb(item_id, res[1]))


@router.callback_query(F.data.startswith("deletechannel_"), IsAdmin())
async def deleted_channel_by_admin(c: CQ, ssn):
    item_id = int(c.data.split("_")[-1])

    res = await channel_deleted(ssn, item_id, "manual")
    if res == "not_found":
        await c.answer("Возникла ошибка", show_alert=True)
        try:
            await c.message.delete()
        except:
            pass

    else:
        try:
            await c.message.delete()
        except:
            await c.answer()
        await c.message.answer(f"✅ Канал <b>{res}</b> удален")
        logging.info(f"Admin {c.from_user.id} deleted channel {res}")
