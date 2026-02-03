import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tmdbv3api import TMDb, Movie, Trending
from dotenv import load_dotenv

load_dotenv()
router = Router()

tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
movie_tool = Movie()
trending_tool = Trending()

# Helper function to format the poster message
def format_movie_msg(movie_data):
    title = movie_data.title
    rating = movie_data.vote_average
    release = getattr(movie_data, 'release_date', 'N/A')[:4]
    overview = movie_data.overview[:300] + "..." if len(movie_data.overview) > 300 else movie_data.overview
    poster = f"https://image.tmdb.org/t/p/w500{movie_data.poster_path}"
    
    caption = (
        f"🎬 **{title.upper()}** ({release})\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"⭐️ **Rating:** `{rating}/10`\n"
        f"📖 **Plot:** _{overview}_"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Search on Google", url=f"https://www.google.com/search?q={title.replace(' ', '+')}+movie")
    
    return poster, caption, builder.as_markup()

@router.message(Command("movie"))
async def get_movie(message: types.Message):
    query = message.text.replace("/movie", "").strip()
    if not query: return await message.reply("🔍 **Usage:** `/movie [name]`")
    
    search = movie_tool.search(query)
    if not search: return await message.reply("❌ No movie found.")
    
    poster, caption, reply_markup = format_movie_msg(search[0])
    await message.reply_photo(photo=poster, caption=caption, reply_markup=reply_markup, parse_mode="Markdown")
