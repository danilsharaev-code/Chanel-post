import datetime as dt
import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Channel, ChannelPost, PostMedia, PostQueue


async def get_post_info(ssn: AsyncSession, post_id):
    ch_post_q = await ssn.execute(
        select(ChannelPost).filter(ChannelPost.id == post_id))
    ch_post_res = ch_post_q.fetchone()
    if ch_post_res is None:
        return "error"

    ch_post: ChannelPost = ch_post_res[0]

    ch_media_q = await ssn.execute(select(PostMedia).filter(
        PostMedia.post_id == post_id).order_by(PostMedia.id))
    ch_media = ch_media_q.scalars().all()

    ch_ids_q = await ssn.execute(select(PostQueue.ch_id).filter(
        PostQueue.post_id == post_id))
    ch_ids = ch_ids_q.scalars().all()

    channels_q = await ssn.execute(
        select(Channel).filter(Channel.id.in_(ch_ids)))
    channels = channels_q.scalars().all()

    return ch_post, ch_media, channels


async def delete_post(ssn: AsyncSession, post_id):
    await ssn.execute(
        delete(ChannelPost).filter(ChannelPost.id == post_id))
    await ssn.execute(
        delete(PostMedia).filter(PostMedia.post_id == post_id))
    await ssn.execute(
        delete(PostQueue).filter(PostQueue.post_id == post_id))
    await ssn.commit()


async def get_all_posts(ssn: AsyncSession):
    posts_q = await ssn.execute(select(ChannelPost).filter(
        ChannelPost.status == "active").order_by(ChannelPost.date_ts))
    posts = posts_q.scalars().all()
    return posts


async def get_channels_by_ids(ssn: AsyncSession, ch_ids):
    channels_q = await ssn.execute(
        select(Channel).filter(Channel.id.in_(ch_ids)))
    channels = channels_q.scalars().all()
    return channels


async def new_post(ssn: AsyncSession, data: dict):
    post_date = dt.datetime.strptime(data['date_digit'], "%d.%m.%Y %H:%M")
    post_ts = int(post_date.timestamp())
    ch_id = 0 if len(data['selected']) > 1 else data['selected'][0]
    new_post = await ssn.merge(ChannelPost(
        ch_id=ch_id, date_ts=post_ts, date_str=data['date_str'],
        media_type=data['media_kind'], media_id=data['media_id'],
        text=data['text']))
    await ssn.commit()
    post_id = new_post.id

    for channel_id in data['selected']:
        await ssn.merge(PostQueue(post_id=post_id, ch_id=channel_id))
    await ssn.commit()

    if len(data['media']) > 0:
        for item in data['media']:
            await ssn.merge(PostMedia(
                post_id=post_id, media_type=item[0], media_id=item[1]))
        await ssn.commit()


async def save_new_post_data(
        ssn: AsyncSession, post_id, text, media_type, media_id, media):
    await ssn.execute(update(ChannelPost).filter(
        ChannelPost.id == post_id).values(
            media_type=media_type, media_id=media_id, text=text))
    await ssn.execute(delete(PostMedia).filter(PostMedia.post_id == post_id))
    await ssn.commit()

    if len(media) > 0:
        for item in media:
            await ssn.merge(PostMedia(
                post_id=post_id, media_type=item[0], media_id=item[1]))
        await ssn.commit()

    ch_post_q = await ssn.execute(
        select(ChannelPost).filter(ChannelPost.id == post_id))
    ch_post: ChannelPost = ch_post_q.fetchone()[0]

    ch_media_q = await ssn.execute(select(PostMedia).filter(
        PostMedia.post_id == post_id).order_by(PostMedia.id))
    ch_media = ch_media_q.scalars().all()

    ch_ids_q = await ssn.execute(select(PostQueue.ch_id).filter(
        PostQueue.post_id == post_id))
    ch_ids = ch_ids_q.scalars().all()

    channels_q = await ssn.execute(
        select(Channel).filter(Channel.id.in_(ch_ids)))
    channels = channels_q.scalars().all()

    return ch_post, ch_media, channels


async def save_new_post_date(ssn: AsyncSession, post_id, date_str, date_digit):
    post_date = dt.datetime.strptime(date_digit, "%d.%m.%Y %H:%M")
    post_ts = int(post_date.timestamp())

    await ssn.execute(update(ChannelPost).filter(
        ChannelPost.id == post_id).values(date_ts=post_ts, date_str=date_str))
    await ssn.commit()

    ch_post_q = await ssn.execute(
        select(ChannelPost).filter(ChannelPost.id == post_id))
    ch_post: ChannelPost = ch_post_q.fetchone()[0]

    ch_media_q = await ssn.execute(select(PostMedia).filter(
        PostMedia.post_id == post_id).order_by(PostMedia.id))
    ch_media = ch_media_q.scalars().all()

    ch_ids_q = await ssn.execute(select(PostQueue.ch_id).filter(
        PostQueue.post_id == post_id))
    ch_ids = ch_ids_q.scalars().all()

    channels_q = await ssn.execute(
        select(Channel).filter(Channel.id.in_(ch_ids)))
    channels = channels_q.scalars().all()

    return ch_post, ch_media, channels


async def get_post_channel_ids(ssn: AsyncSession, post_id):
    ch_ids_q = await ssn.execute(select(PostQueue.ch_id).filter(
        PostQueue.post_id == post_id))
    ch_ids = ch_ids_q.scalars().all()

    channels_q = await ssn.execute(select(Channel).order_by(Channel.id))
    channels = channels_q.scalars().all()
    return ch_ids, channels


async def save_new_post_channels(ssn: AsyncSession, post_id, ch_ids):
    ch_id = 0 if len(ch_ids) > 1 else ch_ids[0]
    await ssn.execute(update(ChannelPost).filter(
        ChannelPost.id == post_id).values(ch_id=ch_id))
    await ssn.execute(delete(PostQueue).filter(
        PostQueue.post_id == post_id))
    await ssn.commit()

    for channel_id in ch_ids:
        await ssn.merge(PostQueue(post_id=post_id, ch_id=channel_id))
    await ssn.commit()

    ch_post_q = await ssn.execute(
        select(ChannelPost).filter(ChannelPost.id == post_id))
    ch_post: ChannelPost = ch_post_q.fetchone()[0]

    ch_media_q = await ssn.execute(select(PostMedia).filter(
        PostMedia.post_id == post_id).order_by(PostMedia.id))
    ch_media = ch_media_q.scalars().all()

    channels_q = await ssn.execute(
        select(Channel).filter(Channel.id.in_(ch_ids)))
    channels = channels_q.scalars().all()

    return ch_post, ch_media, channels
