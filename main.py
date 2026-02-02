import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# Import database & modules
from database import init_db
from modules import admin, movies, tools

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logging.error("❌ No BOT_TOKEN found!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register Routers
    dp.include_router(admin.router)
    dp.include_router(movies.router)
    dp.include_router(tools.router)

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        welcome_text = (
            f"🚀 **AeroMulti-Bot v1.0**\n\n"
            f"Hello {message.from_user.first_name}!\n"
            f"I am your all-in-one assistant. Here's what I can do:\n\n"
            f"🎬 **Movies & Media:**\n"
            f"• `/movie [name]` - Search movie details\n"
            f"• `/trending` - Top 10 movies today\n\n"
            f"🛠️ **Web Tools:**\n"
            f"• `/short [url]` - Shorten links (is.gd)\n"
            f"• `/qr [text/url]` - Generate QR Code\n"
            f"• `/inspect [url]` - Get website source\n\n"
            f"🛡️ **Group Admin:**\n"
            f"• `/autoreaction on/off` - Toggle reactions\n"
        )
        await message.answer(welcome_text, parse_mode="Markdown")

    logging.info("🤖 AeroMulti-Bot has started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
