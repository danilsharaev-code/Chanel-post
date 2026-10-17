from sqlalchemy import (BigInteger, Boolean, Column, DateTime, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import relationship

from db.base import Base


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, autoincrement=True, primary_key=True)
    channel_id = Column(BigInteger)
    title = Column(String(255))


class ChannelPost(Base):
    __tablename__ = 'channelpost'

    id = Column(Integer, autoincrement=True, primary_key=True)

    ch_id = Column(Integer, default=0)

    date_ts = Column(BigInteger)
    date_str = Column(String(50))

    media_type = Column(String(15))
    media_id = Column(String(255))
    text = Column(Text)

    status = Column(String(25), default="active")


class PostMedia(Base):
    __tablename__ = 'postmedia'

    id = Column(Integer, autoincrement=True, primary_key=True)

    post_id = Column(Integer)
    media_type = Column(String(15))
    media_id = Column(String(255))


class PostQueue(Base):
    __tablename__ = 'postqueue'

    id = Column(Integer, autoincrement=True, primary_key=True)

    post_id = Column(Integer)
    ch_id = Column(Integer)
