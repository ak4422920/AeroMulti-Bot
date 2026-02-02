import os
from aiogram import Router, types, F
from aiogram.filters import Command
from tmdbv3api import TMDb, Movie, TV
from dotenv import load_dotenv

load_dotenv()

router = Router()

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
tmdb.language = 'en'
tmdb.debug = True

movie_tool = Movie()
tv_tool = TV()

@router.message(Command("movie"))
async def search_movie(message: types.Message):
    # Extract query from command
    query = message.text.replace("/movie", "").strip()
    
    if not query:
        return await message.reply("❓ Please provide a movie name.\nExample: `/movie Interstellar`", parse_mode="Markdown")

    msg = await message.reply("🔍 Searching TMDb...")
    
    try:
        search = movie_tool.search(query)
        if not search:
            return await msg.edit_text("❌ No movies found.")

        # Get the first (most relevant) result
        res = search[0]
        
        # Build info
        title = res.title
        release = res.release_date[:4] if res.release_date else "N/A"
        rating = res.vote_average
        overview = res.overview[:300] + "..." if len(res.overview) > 300 else res.overview
        poster = f"https://image.tmdb.org/t/p/w500{res.poster_path}" if res.poster_path else None

        caption = (
            f"🎬 **{title}** ({release})\n"
            f"⭐ **Rating:** {rating}/10\n\n"
            f"📝 **Plot:** {overview}\n\n"
            f"🔗 [View on TMDb](https://www.themoviedb.org/movie/{res.id})"
        )

        if poster:
            await message.reply_photo(photo=poster, caption=caption, parse_mode="Markdown")
            await msg.delete()
        else:
            await msg.edit_text(caption, parse_mode="Markdown", disable_web_page_preview=False)

    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

@router.message(Command("trending"))
async def trending_movies(message: types.Message):
    try:
        popular = movie_tool.popular()
        text = "🔥 **Trending Movies Today:**\n\n"
        for i, m in enumerate(popular[:10], 1):
            text += f"{i}. {m.title} ({m.vote_average} ⭐)\n"
        
        await message.reply(text, parse_mode="Markdown")
    except Exception as e:
        await message.reply(f"❌ Error fetching trending: {str(e)}")
      
