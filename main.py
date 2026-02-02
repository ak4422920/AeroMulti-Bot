import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# Import our database connection
from database import init_db

# Import our modules
from modules import admin, movies # Added movies here

# Load variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(level=logging.INFO)

async def main():
    # 1. Initialize MongoDB Connection
    await init_db()

    # 2. Setup Bot and Dispatcher
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logging.error("❌ No BOT_TOKEN found!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 3. Register Routers (Modules)
    dp.include_router(admin.router)
    dp.include_router(movies.router) # Added this line

    # 4. Basic Start Command
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        welcome_text = (
            f"🚀 **AeroMulti-Bot v1.0**\n\n"
            f"Hello {message.from_user.first_name}!\n"
            f"I am your modular assistant. Use the commands below:\n\n"
            f"🎬 **Movies:**\n"
            f"• `/movie [name]` - Search movie info\n"
            f"• `/trending` - Top movies today\n\n"
            f"🛡️ **Admin:**\n"
            f"• `/autoreaction on/off` - Toggle reactions\n"
        )
        await message.answer(welcome_text, parse_mode="Markdown")

    # 5. Start Polling
    logging.info("🤖 AeroMulti-Bot has started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
