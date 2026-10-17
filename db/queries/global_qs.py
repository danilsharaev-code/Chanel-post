import datetime as dt
import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Channel, ChannelPost, PostQueue


async def new_channel(ssn: AsyncSession, channel_id, title):
    await ssn.merge(Channel(channel_id=channel_id, title=title))
    await ssn.commit()


async def channel_deleted(ssn: AsyncSession, channel_id, kind):
    if kind == "auto":
        channnel_q = await ssn.execute(
            select(Channel).filter(Channel.channel_id == channel_id))
    else:
        channnel_q = await ssn.execute(
            select(Channel).filter(Channel.id == channel_id))
    channel_res = channnel_q.fetchone()
    if channel_res:
        channel: Channel = channel_res[0]
        title = channel.title
        await ssn.execute(
            delete(Channel).filter(Channel.id == channel.id))
        await ssn.execute(
            delete(PostQueue).filter(PostQueue.ch_id == channel.id))
        await ssn.execute(
            delete(ChannelPost).filter(ChannelPost.ch_id == channel.id))
        await ssn.commit()
        return title

    else:
        return "not_found"


async def get_channels(ssn: AsyncSession):
    channels_q = await ssn.execute(select(Channel).order_by(Channel.id))
    channels = channels_q.scalars().all()
    return channels


async def get_channel(ssn: AsyncSession, ch_id):
    channnel_q = await ssn.execute(
        select(Channel).filter(Channel.id == ch_id))
    channel: Channel = channnel_q.fetchone()[0]

    post_ids_q = await ssn.execute(select(PostQueue.post_id).filter(
        PostQueue.ch_id == channel.id))
    posts_ids = post_ids_q.scalars().all()

    posts_q = await ssn.execute(select(ChannelPost).filter(
        ChannelPost.id.in_(posts_ids)).filter(
            ChannelPost.status == "active").order_by(ChannelPost.date_ts))
    posts = posts_q.scalars().all()
    return channel, posts


async def get_channel_ids(ssn: AsyncSession):
    channels_q = await ssn.execute(select(Channel.id).order_by(Channel.id))
    channels = channels_q.scalars().all()
    return channels
