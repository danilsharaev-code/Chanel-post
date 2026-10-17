import asyncio
import datetime as dt
import logging
from logging.handlers import TimedRotatingFileHandler

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config_reader import config
from db.base import Base
from handlers import add_post, channels, edit_post_media, posts, start
from middlewares.db import DbSessionMiddleware
from utils.misc import send_scheduled_posts


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Restart Bot"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())


async def main():
    date = dt.datetime.now()

    # Логгирование
    logging.basicConfig(
        handlers=[TimedRotatingFileHandler(
            f"logs/LOGS-{date.day}-{date.month}-{date.year}-{date.hour}-{date.minute}.log", when="d", interval=1)],
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S"
    )

    engine = create_async_engine(
        url=config.db_url.unicode_string(), echo=False,
        pool_size=500, max_overflow=500, pool_timeout=5)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher()

    sheduler = AsyncIOScheduler()
    # sheduler.add_job(send_scheduled_posts, "cron", minute="*/5", second="15",
    #                  args=(sessionmaker, bot))
    sheduler.add_job(send_scheduled_posts, "cron", minute="*/1", second="05",
                     args=(sessionmaker, bot))
    sheduler.start()

    # dp.message.filter(F.chat.type == "private")
    # dp.callback_query.filter(F.message.chat.type == "private")

    # Регистрация роутеров с хэндлерами
    dp.include_router(start.router)
    dp.include_router(add_post.router)
    dp.include_router(edit_post_media.router)
    dp.include_router(channels.router)
    dp.include_router(posts.router)

    # Регистрация мидлварей
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    await set_bot_commands(bot)

    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    logging.getLogger('apscheduler.executors.default').setLevel(
        logging.WARNING)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot, db=sessionmaker,
            allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
