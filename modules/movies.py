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
        return await message.reply("❓ Please provide a movie name.\nExample: `/movie Interstellar`", parse_mode="Markdown")

    msg = await message.reply("🔍 Searching TMDb...")
    
    try:
        search = movie_tool.search(query)
        if not search or len(search) == 0:
            return await msg.edit_text("❌ No movies found.")

        # Get the first result
        res = search[0]
        
        # Safely get attributes
        title = getattr(res, 'title', 'Unknown Title')
        release = getattr(res, 'release_date', '0000')[:4]
        rating = getattr(res, 'vote_average', 0)
        overview = getattr(res, 'overview', 'No description available.')
        if len(overview) > 300:
            overview = overview[:300] + "..."
            
        poster_path = getattr(res, 'poster_path', None)
        poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        caption = (
            f"🎬 **{title}** ({release})\n"
            f"⭐ **Rating:** {rating}/10\n\n"
            f"📝 **Plot:** {overview}\n\n"
            f"🔗 [View on TMDb](https://www.themoviedb.org/movie/{getattr(res, 'id', '')})"
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
    msg = await message.reply("🔥 Fetching today's trending movies...")
    try:
        # Fetch trending movies for the week
        trending = trending_tool.movie_week()
        
        text = "🔥 **Trending Movies This Week:**\n\n"
        
        # Use a simple loop to avoid slice errors
        count = 0
        for m in trending:
            if count >= 10: # Limit to top 10 manually
                break
            
            title = getattr(m, 'title', 'Unknown')
            rating = getattr(m, 'vote_average', 0)
            text += f"{count + 1}. {title} — ⭐ `{rating}`\n"
            count += 1
        
        await msg.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        await msg.edit_text(f"❌ Error fetching trending: {str(e)}")
