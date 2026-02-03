import os
from aiogram import Router, types
from aiogram.filters import Command
from tmdbv3api import TMDb, Movie
from dotenv import load_dotenv

load_dotenv()
router = Router()

# Setup TMDb
tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
movie_tool = Movie()

@router.message(Command("movie"))
async def get_movie(message: types.Message):
    query = message.text.replace("/movie", "").strip()
    if not query:
        return await message.reply("🔍 **Usage:** `/movie [name]`")

    status = await message.reply("🛰️ **Searching...**")
    
    try:
        search = movie_tool.search(query)
        if not search:
            return await status.edit_text("❌ No movie found.")

        res = search[0]
        title = res.title
        rating = res.vote_average
        release = getattr(res, 'release_date', 'N/A')[:4]
        overview = res.overview[:300] + "..." if len(res.overview) > 300 else res.overview
        poster = f"https://image.tmdb.org/t/p/w500{res.poster_path}"

        caption = (
            f"🎬 **{title.upper()}** ({release})\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"⭐️ **Rating:** `{rating}/10`\n"
            f"📖 **Plot:** _{overview}_"
        )

        await message.reply_photo(photo=poster, caption=caption, parse_mode="Markdown")
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: `{e}`")
