import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tmdbv3api import TMDb, Movie
from dotenv import load_dotenv

load_dotenv()
router = Router()

# TMDb Setup
tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
movie_tool = Movie()

def get_movie_layout(res):
    """Generates the poster, caption, and buttons for any movie object"""
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
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🍿 TMDb Info", url=f"https://www.themoviedb.org/movie/{res.id}")
    return poster, caption, builder.as_markup()

@router.message(Command("movie"))
async def search_movie(message: types.Message):
    query = message.text.replace("/movie", "").strip()
    if not query:
        return await message.reply("🔍 **Usage:** `/movie [name]`")
    
    search = movie_tool.search(query)
    if not search:
        return await message.reply("❌ No results found.")
    
    poster, caption, markup = get_movie_layout(search[0])
    await message.reply_photo(photo=poster, caption=caption, reply_markup=markup, parse_mode="Markdown")
