import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
from database import test_db_connection, is_movie_posted, save_posted_movie
from tmdbv3api import Trending

# Import movie router and layout
from modules.movies import router as movie_router, get_movie_layout

logging.basicConfig(level=logging.INFO)

# --- Koyeb Health Check ---
async def handle(request):
    return web.Response(text="Bot is Running")

async def start_health_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8000).start()

# --- Autopost Background Task ---
async def movie_autopost(bot: Bot):
    trending_tool = Trending()
    channel_id = os.getenv("MOVIE_CHANNEL_ID")
    
    while True:
        if channel_id:
            try:
                # Fetch daily trending
                trending = trending_tool.movie_day()
                for movie in trending[:5]: # Check top 5 movies
                    if not await is_movie_posted(movie.id):
                        poster, caption, markup = get_movie_layout(movie)
                        await bot.send_photo(
                            chat_id=channel_id, 
                            photo=poster, 
                            caption=f"🔥 **NEW TRENDING UPDATE**\n\n{caption}", 
                            reply_markup=markup, 
                            parse_mode="Markdown"
                        )
                        await save_posted_movie(movie.id)
                        logging.info(f"✅ Posted new movie: {movie.title}")
                        break # Post only one new movie per cycle
            except Exception as e:
                logging.error(f"Autopost Error: {e}")
        
        # Check every 12 hours (43200 seconds)
        await asyncio.sleep(43200)

async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        logging.error("No BOT_TOKEN found!")
        return

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Register Routers
    dp.include_router(movie_router)

    @dp.message(CommandStart())
    async def start_cmd(message: types.Message):
        is_db_up = await test_db_connection()
        status = "✅ Connected" if is_db_up else "❌ Failed"
        await message.answer(f"🚀 **AeroMulti v2.0 Ready!**\n\n🗄️ **Database:** {status}\n🎬 **Autopost:** Active")

    # Start Services
    asyncio.create_task(start_health_server())
    asyncio.create_task(movie_autopost(bot))
    
    logging.info("🤖 Bot Starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
