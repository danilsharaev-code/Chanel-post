from aiogram.filters.callback_data import CallbackData
from aiogram.types import (ChatAdministratorRights, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton,
                           KeyboardButtonRequestChat, ReplyKeyboardMarkup)

cancel_btn = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отменить", callback_data="cancel_cb")
        ]
    ]
)

close_btn = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅", callback_data="close")
        ]
    ]
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Создать пост"),
            KeyboardButton(text="Мои посты")
        ],
        [
            KeyboardButton(text="Добавить канал", request_chat=KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=True,
                user_administrator_rights=ChatAdministratorRights(
                    is_anonymous=False,
                    can_manage_chat=False,
                    can_delete_messages=True,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_promote_members=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_post_stories=False,
                    can_edit_stories=False,
                    can_delete_stories=False,
                    can_post_messages=True,
                    can_edit_messages=True),
                bot_administrator_rights=ChatAdministratorRights(
                    is_anonymous=False,
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=True,
                    can_post_stories=False,
                    can_edit_stories=False,
                    can_delete_stories=False,
                    can_post_messages=True,
                    can_edit_messages=True
                ))),
            KeyboardButton(text="Мои каналы")
        ],
    ],
    resize_keyboard=True
)
