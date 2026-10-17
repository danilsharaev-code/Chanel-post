import datetime as dt
import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Channel, ChannelPost, PostMedia, PostQueue


async def get_posts_to_send(db):
    ssn: AsyncSession
    async with db() as ssn:
        date = dt.datetime.now()
        date_ts = int(date.timestamp())

        posts_q = await ssn.execute(select(ChannelPost).filter(
            ChannelPost.date_ts <= date_ts).filter(
                ChannelPost.status == "active"))
        posts = posts_q.scalars().all()
        return posts


async def get_post_data(db, post_id):
    ssn: AsyncSession
    async with db() as ssn:
        post_media_q = await ssn.execute(select(PostMedia).filter(
            PostMedia.post_id == post_id).order_by(PostMedia.id))
        post_media = post_media_q.scalars().all()

        ch_ids_q = await ssn.execute(select(PostQueue.ch_id).filter(
            PostQueue.post_id == post_id))
        ch_ids = ch_ids_q.scalars().all()

        channels_q = await ssn.execute(
            select(Channel).filter(Channel.id.in_(ch_ids)))
        channels = channels_q.scalars().all()

        await ssn.execute(update(ChannelPost).filter(
            ChannelPost.id == post_id).values(status="sent"))
        await ssn.commit()

        return post_media, channels
