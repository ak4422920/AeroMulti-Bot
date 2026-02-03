import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from tmdbv3api import Trending
from modules.movies import format_movie_msg, router as movie_router
from database import init_db
from aiohttp import web

# --- Autopost Logic ---
async def movie_autopost(bot: Bot):
    trending_tool = Trending()
    channel_id = os.getenv("MOVIE_CHANNEL_ID")
    
    while True:
        if channel_id:
            try:
                # Get current trending movies
                trending = trending_tool.movie_day()
                if trending:
                    # Post the top trending movie of the day
                    poster, caption, markup = format_movie_msg(trending[0])
                    await bot.send_photo(chat_id=channel_id, photo=poster, caption=f"🔥 **DAILY TRENDING POST**\n\n{caption}", reply_markup=markup, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Autopost Error: {e}")
        
        # Wait 12 hours before next post (43200 seconds)
        await asyncio.sleep(43200)

# --- Standard Boilerplate ---
async def handle(request): return web.Response(text="Bot Alive")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8000).start()

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(movie_router)

    # Start the Autopost task in the background
    asyncio.create_task(movie_autopost(bot))
    asyncio.create_task(start_server())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
