import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from database import init_db
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Start the Database
    await init_db()

    # Initialize Bot & Dispatcher
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # A simple test command
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        await message.answer(
            f"🚀 **AeroMulti-Bot** is online!\n"
            f"Ready to serve on the go, {message.from_user.first_name}."
        )

    print("🤖 AeroMulti-Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

