from textwrap import dedent

from db.models import Channel, ChannelPost


def format_post_text(ch_post: ChannelPost, channels):
    txt = f"⬆️\n<b>Дата публикации:</b> {ch_post.date_str}\n\n"
    txt += "<b>Каналы для публикации:</b>"
    chnl: Channel
    for chnl in channels:
        txt += f"\n{chnl.title}"

    return txt


def format_pre_created_post_text(date_str, channels):
    txt = f"⬆️\n<b>Дата публикации:</b> {date_str}\n\n"
    txt += "<b>Каналы для публикации:</b>"
    chnl: Channel
    for chnl in channels:
        txt += f"\n{chnl.title}"

    return txt
