import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# Import our database connection
from database import init_db

# Import our modules (We will add more here in Step 3, 4, etc.)
from modules import admin

# Load variables from .env file
load_dotenv()

# Enable logging to see errors in the console/hosting logs
logging.basicConfig(level=logging.INFO)

async def main():
    # 1. Initialize MongoDB Connection
    await init_db()

    # 2. Setup Bot and Dispatcher
    # We get the token from Environment Variables for security
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("❌ ERROR: No BOT_TOKEN found in environment variables!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 3. Register Routers (Modules)
    # This connects the code in modules/admin.py to the bot
    dp.include_router(admin.router)

    # 4. Basic Start Command
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        # Professional welcome message
        welcome_text = (
            f"🚀 **AeroMulti-Bot v1.0 is Online!**\n\n"
            f"Hello {message.from_user.first_name}! I am your modular "
            f"multitasking assistant powered by MongoDB.\n\n"
            f"💡 **Available Modules:**\n"
            f"• Group Admin (Auto-Reactions)\n"
            f"• More coming soon..."
        )
        await message.answer(welcome_text, parse_mode="Markdown")

    # 5. Start Polling
    print("🤖 AeroMulti-Bot has started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
