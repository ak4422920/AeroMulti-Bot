import os
from aiogram import Router, types
from aiogram.filters import Command
from tmdbv3api import TMDb, Movie, Trending
from dotenv import load_dotenv

load_dotenv()
router = Router()

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
tmdb.language = 'en'

movie_tool = Movie()
trending_tool = Trending()

@router.message(Command("movie"))
async def search_movie(message: types.Message):
    query = message.text.replace("/movie", "").strip()
    
    if not query:
        return await message.reply("🍿 **Usage:** `/movie [title]`")

    msg = await message.reply("🛰️ **Scanning TMDb database...**")
    
    try:
        search = movie_tool.search(query)
        if not search:
            return await msg.edit_text("❌ No results found for your search.")

        res = search[0]
        title = getattr(res, 'title', 'N/A')
        release = getattr(res, 'release_date', 'N/A')[:4]
        rating = getattr(res, 'vote_average', 0)
        overview = getattr(res, 'overview', 'No plot available.')
        
        # UI Formatting
        if len(overview) > 400:
            overview = overview[:400] + "..."

        poster_path = getattr(res, 'poster_path', None)
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        caption = (
            f"🎬 **{title.upper()}**\n\n"
            f"📅 **Year:** `{release}`\n"
            f"🌟 **Rating:** `⭐ {rating}/10`\n\n"
            f"📖 **Storyline:**\n_{overview}_\n\n"
            f"Powered by @{message.bot.user.username if message.bot.user else 'AeroMulti'}"
        )

        if poster_url:
            await message.reply_photo(photo=poster_url, caption=caption, parse_mode="Markdown")
            await msg.delete()
        else:
            await msg.edit_text(caption, parse_mode="Markdown")

    except Exception as e:
        await msg.edit_text(f"❌ **TMDb Error:** `{str(e)}`")

@router.message(Command("trending"))
async def trending_movies(message: types.Message):
    msg = await message.reply("🔥 **Fetching trending media...**")
    try:
        trending = trending_tool.movie_week()
        text = "🏆 **TRENDING THIS WEEK** 🏆\n\n"
        
        count = 0
        for m in trending:
            if count >= 10: break
            title = getattr(m, 'title', 'Unknown')
            rating = getattr(m, 'vote_average', 0)
            text += f"**{count + 1}.** {title} — `⭐ {rating}`\n"
            count += 1
        
        await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
