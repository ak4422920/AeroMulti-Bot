import os
import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from yt_dlp import YoutubeDL

router = Router()

@router.message(Command("song"))
async def song_finder(message: types.Message):
    query = message.text.replace("/song", "").strip()
    
    if not query:
        return await message.reply("❓ Please provide a song name.\nExample: `/song Blinding Lights`")

    status_msg = await message.reply(f"🔍 Searching for `{query}`...")

    # yt-dlp Configuration for Audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1', # Search YouTube and take first result
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    try:
        loop = asyncio.get_event_loop()
        # Extract info and download
        info = await loop.run_in_executor(None, lambda: YoutubeDL(ydl_opts).extract_info(query, download=True))
        
        # The result of a search is inside 'entries'
        video_data = info['entries'][0]
        file_name = f"downloads/{video_data['title']}.mp3"

        await status_msg.edit_text("📤 Uploading audio...")

        # Send as Audio file (so it appears in music players)
        audio_file = types.FSInputFile(file_name)
        await message.reply_audio(
            audio=audio_file,
            title=video_data.get('title'),
            performer=video_data.get('uploader'),
            caption=f"🎵 **Found:** `{video_data['title']}`"
        )

        # Cleanup
        os.remove(file_name)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Could not find song. Error: `{str(e)[:50]}`")
