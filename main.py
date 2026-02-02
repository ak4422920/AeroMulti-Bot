import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiohttp import web

# Import database
from database import init_db

# Import all modules
from modules import (
    admin, movies, tools, files, downloader, 
    reputation, afk, night_mode, mediainfo, osint, song, logs, youtube
)
from modules.middleware import ForceSubMiddleware

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def handle(request):
    return web.Response(text="Bot is Running!")

async def start_webhook():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()

async def main():
    await init_db()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.outer_middleware(ForceSubMiddleware())

    # Register All Routers
    dp.include_router(admin.router)
    dp.include_router(movies.router)
    dp.include_router(tools.router)
    dp.include_router(files.router)
    dp.include_router(downloader.router)
    dp.include_router(reputation.router)
    dp.include_router(afk.router)
    dp.include_router(night_mode.router)
    dp.include_router(mediainfo.router)
    dp.include_router(osint.router)
    dp.include_router(song.router)
    dp.include_router(youtube.router)

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message, command=None):
        await logs.send_log(bot, message, "Started the Bot")
        welcome_text = (
            f"🚀 **AeroMulti-Bot v1.0**\n\n"
            f"Hello {message.from_user.first_name}!\n\n"
            f"📺 **YouTube:** `/youtube [query]`\n"
            f"🎵 **Music:** `/song [name]`\n"
            f"📥 **Downloader:** Paste social link\n"
            f"🎬 **Media:** `/movie`, `/trending`\n"
            f"🛠️ **Tools:** `/short`, `/qr`, `/me`"
        )
        await message.answer(welcome_text, parse_mode="Markdown")

    asyncio.create_task(start_webhook())
    logging.info("🤖 AeroMulti-Bot is fully loaded!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
