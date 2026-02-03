import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
from database import init_db

# --- Koyeb Health Check ---
async def handle(request):
    return web.Response(text="Bot is Alive")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8000).start()

# --- Bot Logic ---
async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: types.Message):
        db_status = await init_db()
        status_text = "✅ Connected" if db_status else "❌ Failed"
        await message.answer(f"🚀 **AeroMulti v2.0 Online!**\n\n🗄️ **Database:** {status_text}\n\nSend /me to test next.")

    # Start health server and bot
    asyncio.create_task(start_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
