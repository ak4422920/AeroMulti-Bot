import io
import aiohttp
import qrcode
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

router = Router()

# --- 🔗 URL SHORTENER (Using is.gd) ---
@router.message(Command("short"))
async def short_url(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❓ Please provide a URL.\nExample: `/short https://www.google.com`", parse_mode="Markdown")
    
    long_url = args[1]
    # is.gd is a great, free, no-key-needed alternative to TinyURL
    api_url = f"https://is.gd/create.php?format=simple&url={long_url}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                if response.status == 200:
                    shortened = await response.text()
                    await message.reply(
                        f"✅ **URL Shortened!**\n\n🔗 **Original:** `{long_url}`\n🚀 **Short:** {shortened}", 
                        disable_web_page_preview=True,
                        parse_mode="Markdown"
                    )
                else:
                    await message.reply("❌ Failed to shorten URL. is.gd might be down or the link is invalid.")
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")

# --- 🖼️ QR CODE GENERATOR ---
@router.message(Command("qr"))
async def make_qr(message: types.Message):
    data = message.text.replace("/qr", "").strip()
    if not data:
        return await message.reply("❓ Please provide text or a link.\nExample: `/qr https://google.com`")

    msg = await message.reply("🖼️ Generating QR Code...")
    
    # Generate QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to memory
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    file = BufferedInputFile(buf.read(), filename="qrcode.png")
    await message.reply_photo(photo=file, caption=f"✅ QR Code for:\n`{data}`", parse_mode="Markdown")
    await msg.delete()

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
