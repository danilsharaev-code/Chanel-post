from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, ChatMemberUpdated, Message

from utils.const import admin_ids


class IsAdmin(BaseFilter):
    async def __call__(self, target: Union[Message, CallbackQuery, ChatMemberUpdated]):
        return target.from_user.id in admin_ids
