import os
import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from yt_dlp import YoutubeDL

router = Router()

# Create a downloads folder if it doesn't exist
if not os.path.exists("downloads"):
    os.makedirs("downloads")

@router.message(F.text.startswith("http"))
async def link_handler(message: types.Message):
    url = message.text.strip()
    
    # Simple check to see if it's a supported social media link
    supported_sites = ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "x.com", "twitter.com", "facebook.com"]
    if not any(site in url for site in supported_sites):
        return # Ignore other links

    status_msg = await message.reply("⏳ **Processing link...**\nFetching video data from the cloud.")

    # yt-dlp Configuration
    # We restrict to 50MB to avoid Telegram Bot API errors
    ydl_opts = {
        'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # Run yt-dlp in a thread so it doesn't freeze the bot
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: YoutubeDL(ydl_opts).extract_info(url, download=True))
        
        file_path = YoutubeDL(ydl_opts).prepare_filename(info)

        if os.path.exists(file_path):
            await status_msg.edit_text("📤 **Uploading to Telegram...**")
            
            video = types.FSInputFile(file_path)
            await message.reply_video(
                video=video, 
                caption=f"✅ **Downloaded successfully!**\n\n🎬 **Title:** {info.get('title', 'Video')}\n🌐 **Source:** {info.get('extractor_key', 'Web')}"
            )
            
            # Cleanup: Delete file after sending
            os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Failed to download. The file might be too large (>50MB).")

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** Video might be private, age-restricted, or too large.\n\n`{str(e)[:100]}`")
