import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from database import init_db
from modules import admin, movies, tools, files, downloader, reputation, afk, night_mode, mediainfo, osint

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register Routers
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

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message, command=None):
        if not (command and command.args):
            welcome_text = (
                f"🚀 **AeroMulti-Bot v1.0**\n"
                f"Hello {message.from_user.first_name}!\n\n"
                f"📥 **Downloader:** Paste any social link!\n"
                f"🎬 **Media:** `/movie`, `/mediainfo` (reply)\n"
                f"🛠️ **Tools:** `/short`, `/qr`, `/github` [user]\n"
                f"📁 **File Sharing:** Send a file for a link!\n"
                f"🏆 **Karma:** `/top` leaderboard\n"
                f"🛡️ **Admin:** `/autoreaction`, `/nightmode`"
            )
            await message.answer(welcome_text, parse_mode="Markdown")

    logging.info("🤖 AeroMulti-Bot has started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
