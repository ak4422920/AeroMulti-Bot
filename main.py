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

# --- DUMMY WEB SERVER FOR KOYEB ---
async def handle(request):
    return web.Response(text="Bot is Online and Healthy")

async def start_webhook():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()

# --- MAIN BOT LOGIC ---
async def main():
    await init_db()
    
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 1. Force Sub Middleware (Checked first)
    dp.message.outer_middleware(ForceSubMiddleware())

    # 2. Register Routers in order of priority (CRITICAL)
    # Commands must come BEFORE catch-all handlers
    dp.include_router(admin.router)
    dp.include_router(movies.router)
    dp.include_router(song.router)
    dp.include_router(youtube.router)
    dp.include_router(osint.router)
    dp.include_router(tools.router)
    dp.include_router(reputation.router)
    dp.include_router(night_mode.router)
    dp.include_router(mediainfo.router)
    dp.include_router(files.router)
    
    # These two stay at the bottom because they process general text
    dp.include_router(downloader.router)
    dp.include_router(afk.router)

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message, command=None):
        await logs.send_log(bot, message, "Used /start")
        welcome_text = (
            f"🚀 **AERO MULTI-TOOL BOT v1.1**\n\n"
            f"Hello {message.from_user.first_name}! All systems are **Operational**.\n\n"
            f"🎬 **Media:** `/movie`, `/trending`, `/song`, `/youtube`\n"
            f"🛠️ **Tools:** `/short`, `/qr`, `/mediainfo` (reply)\n"
            f"🕵️ **OSINT:** `/me` (reply), `/github`, `/ip`\n"
            f"📥 **DL:** Paste any TikTok/YT link directly!"
        )
        await message.answer(welcome_text, parse_mode="Markdown")

    # Start Health Check Server
    asyncio.create_task(start_webhook())
    
    logging.info("🤖 AeroMulti-Bot: Polling Started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot offline.")
