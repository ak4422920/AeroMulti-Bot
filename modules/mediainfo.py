import os
from aiogram import Router, types, F
from aiogram.filters import Command
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

router = Router()

@router.message(Command("mediainfo"))
async def get_mediainfo(message: types.Message, bot):
    # Check if user replied to a video/document
    reply = message.reply_to_message
    if not reply or not (reply.video or reply.document or reply.audio):
        return await message.reply("❓ Please reply to a video, audio, or document file with `/mediainfo`.")

    status = await message.reply("⏳ Analyzing file metadata...")

    # Determine file_id
    media = reply.video or reply.document or reply.audio
    file_id = media.file_id

    # Download the file locally
    file = await bot.get_file(file_id)
    file_path = f"downloads/{file_id}"
    await bot.download_file(file.file_path, file_path)

    try:
        # Parse metadata
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        
        if not metadata:
            return await status.edit_text("❌ Could not extract metadata from this file.")

        info = "📄 **Media Technical Info**\n\n"
        for line in metadata.exportPlaintext():
            if "-" not in line: # Filter out empty headers
                info += f"• {line}\n"
        
        # Add basic file size
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        info += f"\n📦 **File Size:** `{size_mb:.2f} MB`"

        await status.edit_text(info, parse_mode="Markdown")

    except Exception as e:
        await status.edit_text(f"❌ **Error:** {str(e)}")
    
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        if parser:
            parser.close()
