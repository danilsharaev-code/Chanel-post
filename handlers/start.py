from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext as FSM
from aiogram.types import CallbackQuery as CQ
from aiogram.types import Message as Mes

from keyboards.main_kbs import main_kb
from utils.const import admin_ids

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


@router.message(Command("start"))
async def start_cmd(m: Mes, state: FSM):
    await state.clear()
    if m.from_user.id in admin_ids:
        await m.answer("⭐️ Админ-меню", reply_markup=main_kb)
    else:
        await m.answer("✋")


@router.callback_query(F.data == "cancel_cb")
async def cancel_cb_cmd(c: CQ, state: FSM):
    await state.clear()

    try:
        await c.message.delete()
    except:
        pass

    await c.answer()


@router.callback_query(F.data == "close")
async def close_window(c: CQ):
    try:
        await c.message.delete()
    except:
        pass

    await c.answer()
