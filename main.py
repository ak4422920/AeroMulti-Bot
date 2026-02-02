import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# Import database
from database import init_db

# Import all modules
from modules import (
    admin, movies, tools, files, downloader, 
    reputation, afk, night_mode, mediainfo, osint, song, logs
)
from modules.middleware import ForceSubMiddleware

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logging.error("❌ NO BOT_TOKEN FOUND!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # --- Register Middleware (Force Subscribe) ---
    dp.message.outer_middleware(ForceSubMiddleware())

    # --- Register All Routers ---
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

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message, command=None):
        # Log this activity
        await logs.send_log(bot, message, "Used /start command")

        if not (command and command.args):
            welcome_text = (
                f"🚀 **AeroMulti-Bot v1.0**\n\n"
                f"Hello {message.from_user.first_name}! Your all-in-one assistant is ready.\n\n"
                f"🎵 **Music:** `/song [name]`\n"
                f"📥 **Downloader:** Paste any social link\n"
                f"🎬 **Media:** `/movie`, `/trending`, `/mediainfo`\n"
                f"🕵️ **OSINT:** `/me`, `/github`, `/ip`\n"
                f"🛠️ **Tools:** `/short`, `/qr`, `/inspect`\n"
                f"📁 **Files:** Send a file for a link\n"
                f"🏆 **Social:** `/top` karma, `/afk` status\n"
                f"🛡️ **Admin:** `/autoreaction`, `/nightmode`"
            )
            await message.answer(welcome_text, parse_mode="Markdown")

    logging.info("🤖 AeroMulti-Bot is fully loaded and running!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot offline.")
