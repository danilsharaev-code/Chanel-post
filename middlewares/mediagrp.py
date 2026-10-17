import asyncio
from typing import Any, Awaitable, Callable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}
    album_caption: dict = {}

    def __init__(self, latency: Union[int, float] = 1):
        self.latency = latency

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: dict[str, Any]
    ) -> Any:
        if not message.media_group_id:
            await handler(message, data)
            return

        if message.caption:
            caption = message.html_text
        else:
            caption = "no_text"

        if message.photo:
            try:
                self.album_data[message.media_group_id].append(
                    (message.message_id, "image", message.photo[-1].file_id)
                )

                curr_caption = self.album_caption[message.media_group_id]
                if curr_caption == "no_text":
                    self.album_caption[message.media_group_id] = caption
            except KeyError:
                self.album_data[message.media_group_id] = [
                    (message.message_id, "image", message.photo[-1].file_id)
                ]
                self.album_caption[message.media_group_id] = caption
                await asyncio.sleep(self.latency)

                self.album_data[message.media_group_id].sort(key=lambda x: x[0])
                album = [[item[1], item[2]] for item in self.album_data[message.media_group_id]]

                data['_is_last'] = True
                data["album"] = album
                data["captions"] = self.album_caption[message.media_group_id]
                await handler(message, data)

        elif message.video:
            try:
                self.album_data[message.media_group_id].append(
                    (message.message_id, "video", message.video.file_id)
                )

                curr_caption = self.album_caption[message.media_group_id]
                if curr_caption == "no_text":
                    self.album_caption[message.media_group_id] = caption
            except KeyError:
                self.album_data[message.media_group_id] = [
                    (message.message_id, "video", message.video.file_id)
                ]
                self.album_caption[message.media_group_id] = caption
                await asyncio.sleep(self.latency)

                self.album_data[message.media_group_id].sort(key=lambda x: x[0])
                album = [[item[1], item[2]] for item in self.album_data[message.media_group_id]]

                data['_is_last'] = True
                data["album"] = album
                data["captions"] = self.album_caption[message.media_group_id]
                await handler(message, data)

        if message.media_group_id and data.get("_is_last"):
            del self.album_data[message.media_group_id]
            del self.album_caption[message.media_group_id]
            del data['_is_last']
