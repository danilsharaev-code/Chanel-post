import asyncio
import datetime
import logging

from aiogram import Bot, types

from db.models import Channel, ChannelPost, PostMedia
from db.queries.scheduled_qs import get_post_data, get_posts_to_send
from utils.const import admin_ids, month_list


async def delete_prev_message(bot: Bot, user_id, msg_id):
    if msg_id:
        await bot.delete_message(user_id, msg_id)


async def send_post(ch_post: ChannelPost, ch_media, bot: Bot, chat_id):
    status = "not_sent"

    if ch_post.media_type == "text":
        try:
            await bot.send_message(chat_id, text=ch_post.text)
            status = "sent"
        except Exception as error:
            logging.error(
                f"Send error post {ch_post.id} to chat {chat_id}: {error}")
    else:
        if ch_post.text == "no_text":
            caption = None
        else:
            caption = ch_post.text

        if ch_post.media_type == "image":
            try:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=ch_post.media_id, caption=caption)
                status = "sent"
            except Exception as error:
                logging.error(
                    f"Send error post {ch_post.id} to chat {chat_id}: {error}")
        elif ch_post.media_type == "video":
            try:
                await bot.send_video(
                    chat_id=chat_id,
                    video=ch_post.media_id, caption=caption)
                status = "sent"
            except Exception as error:
                logging.error(
                    f"Send error post {ch_post.id} to chat {chat_id}: {error}")
        elif ch_post.media_type == "audio":
            try:
                await bot.send_audio(
                    chat_id=chat_id,
                    audio=ch_post.media_id, caption=caption)
                status = "sent"
            except Exception as error:
                logging.error(
                    f"Send error post {ch_post.id} to chat {chat_id}: {error}")
        elif ch_post.media_type == "voice":
            try:
                await bot.send_voice(
                    chat_id=chat_id,
                    voice=ch_post.media_id, caption=caption)
                status = "sent"
            except Exception as error:
                logging.error(
                    f"Send error post {ch_post.id} to chat {chat_id}: {error}")
        elif ch_post.media_type == "video_note":
            try:
                await bot.send_video_note(
                    chat_id=chat_id, video_note=ch_post.media_id)
                status = "sent"
            except Exception as error:
                logging.error(
                    f"Send error post {ch_post.id} to chat {chat_id}: {error}")
        else:
            media = []
            item: PostMedia
            for num, item in enumerate(ch_media, start=1):
                if num == len(ch_media):
                    if item.media_type == "video":
                        media.append(types.InputMediaVideo(
                            media=item.media_id, caption=caption))
                    else:
                        media.append(types.InputMediaPhoto(
                            media=item.media_id, caption=caption))
                else:
                    if item.media_type == "video":
                        media.append(types.InputMediaVideo(
                            media=item.media_id))
                    else:
                        media.append(types.InputMediaPhoto(
                            media=item.media_id))

            try:
                await bot.send_media_group(chat_id=chat_id, media=media)
                status = "sent"
            except Exception as error:
                logging.error(
                    f"Send error post {ch_post.id} to chat {chat_id}: {error}")

    return status


async def send_pre_created_post(text, media_type, media_id, ch_media, bot: Bot, chat_id):
    status = "not_sent"

    if media_type == "text":
        try:
            await bot.send_message(chat_id, text=text)
            status = "sent"
        except Exception as error:
            logging.error(f"Send error: {error}")
    else:
        if text == "no_text":
            caption = None
        else:
            caption = text

        if media_type == "image":
            try:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=media_id, caption=caption)
                status = "sent"
            except Exception as error:
                logging.error(f"Send error : {error}")
        elif media_type == "video":
            try:
                await bot.send_video(
                    chat_id=chat_id,
                    video=media_id, caption=caption)
                status = "sent"
            except Exception as error:
                logging.error(f"Send error: {error}")
        elif media_type == "audio":
            try:
                await bot.send_audio(
                    chat_id=chat_id,
                    audio=media_id, caption=caption)
                status = "sent"
            except Exception as error:
                logging.error(f"Send error: {error}")
        elif media_type == "voice":
            try:
                await bot.send_voice(
                    chat_id=chat_id,
                    voice=media_id, caption=caption)
                status = "sent"
            except Exception as error:
                logging.error(f"Send error: {error}")
        elif media_type == "video_note":
            try:
                await bot.send_video_note(
                    chat_id=chat_id, video_note=media_id)
                status = "sent"
            except Exception as error:
                logging.error(f"Send error: {error}")
        else:
            media = []
            for num, item in enumerate(ch_media, start=1):
                if num == len(ch_media):
                    if item[0] == "video":
                        media.append(types.InputMediaVideo(
                            media=item[1], caption=caption))
                    else:
                        media.append(types.InputMediaPhoto(
                            media=item[1], caption=caption))
                else:
                    if item[0] == "video":
                        media.append(types.InputMediaVideo(
                            media=item[1]))
                    else:
                        media.append(types.InputMediaPhoto(
                            media=item[1]))

            try:
                await bot.send_media_group(chat_id=chat_id, media=media)
                status = "sent"
            except Exception as error:
                logging.error(f"Send error: {error}")

    return status


def check_input_date(date_txt):
    try:
        deadline_date = datetime.datetime.strptime(date_txt, "%d.%m.%Y %H:%M")
    except:
        deadline_date = "error"

    if deadline_date == "error":
        return "error"

    now_date = datetime.datetime.now()
    now_ts = int(now_date.timestamp())

    deadline_ts = int(deadline_date.timestamp())
    if deadline_ts <= now_ts:
        return "error"
    deadline_str = f"{deadline_date.day} {month_list[deadline_date.month - 1]} {deadline_date.year}"
    deadline_digit = deadline_date.strftime("%d.%m.%Y")

    return deadline_ts, deadline_str, deadline_digit


async def send_scheduled_posts(db, bot: Bot):
    posts = await get_posts_to_send(db)
    if len(posts) > 0:
        ch_post: ChannelPost
        for ch_post in posts:
            post_data = await get_post_data(db, ch_post.id)
            channel: Channel
            for channel in post_data[1]:
                res = await send_post(
                    ch_post, post_data[0], bot, channel.channel_id)
                if res == "sent":
                    logging.info(
                        f"Post {ch_post.id} sent to channel {channel.channel_id} {channel.title}")
                # if res == "sent":
                #     txt = f"✅ Пост опубликован в канале <b>{channel.title}</b>"
                # else:
                #     txt = f"⚠️ Возникла ошибка публикации в канале <b>{channel.title}</b>"

                # for admin_id in admin_ids:
                #     try:
                #         await bot.send_message(admin_id, txt)
                #     except:
                #         pass
                #         await asyncio.sleep(.3)

                await asyncio.sleep(2.7)
