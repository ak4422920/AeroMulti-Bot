import io
import aiohttp
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

router = Router()

# --- 🔗 URL SHORTENER ---
@router.message(Command("short"))
async def short_url(message: types.Message):
    # Extract the URL from the command
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❓ Please provide a URL.\nExample: `/short https://www.google.com`", parse_mode="Markdown")
    
    long_url = args[1]
    api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                if response.status == 200:
                    shortened = await response.text()
                    await message.reply(f"🔗 **Shortened URL:**\n{shortened}", disable_web_page_preview=True)
                else:
                    await message.reply("❌ Failed to shorten URL. Make sure it's a valid link.")
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")

# --- 🌐 WEBSITE SOURCE DOWNLOADER ---
@router.message(Command("inspect"))
async def inspect_website(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❓ Please provide a website URL.\nExample: `/inspect https://python.org`")

    url = args[1]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    msg = await message.reply("📡 Fetching website source...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return await msg.edit_text(f"❌ Could not fetch site. Status code: {response.status}")
                
                source_code = await response.text()
                
                # Convert string to bytes for a file upload
                file_content = source_code.encode('utf-8')
                document = BufferedInputFile(file_content, filename="source.html")
                
                await message.reply_document(
                    document=document,
                    caption=f"📄 **Source Code for:**\n`{url}`",
                    parse_mode="Markdown"
                )
                await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Error: {str(e)}")
