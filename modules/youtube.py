import os
import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from yt_dlp import YoutubeDL

router = Router()

@router.message(Command("youtube"))
async def youtube_search(message: types.Message):
    query = message.text.replace("/youtube", "").strip()
    
    if not query:
        return await message.reply("❓ Please provide a search query.\nExample: `/youtube lofi hip hop`", parse_mode="Markdown")

    status_msg = await message.reply("🔍 Searching YouTube...")

    # yt-dlp Configuration for searching
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True, # Only get metadata, don't download
        'default_search': 'ytsearch5', # Get top 5 results
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            
        if not info or 'entries' not in info:
            return await status_msg.edit_text("❌ No results found.")

        results_text = f"📺 **YouTube Results for:** `{query}`\n\n"
        
        for i, entry in enumerate(info['entries'], 1):
            title = entry.get('title', 'Unknown')
            url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
            uploader = entry.get('uploader', 'Unknown Channel')
            duration = entry.get('duration_string', 'N/A')
            
            results_text += (
                f"{i}. **{title}**\n"
                f"👤 {uploader} | 🕒 {duration}\n"
                f"🔗 [Watch Video]({url})\n\n"
            )

        await status_msg.edit_text(results_text, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        await status_msg.edit_text(f"❌ **Search Error:** `{str(e)[:100]}`")
