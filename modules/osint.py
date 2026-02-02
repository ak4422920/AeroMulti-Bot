import aiohttp
from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()

# --- 🆔 USER INFO (ME) FUNCTION ---
@router.message(Command("me"))
async def user_info(message: types.Message):
    # Check if command is a reply to someone else
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    
    info = (
        f"👤 **User Information**\n\n"
        f"🏷️ **First Name:** {target.first_name}\n"
        f"🆔 **User ID:** `{target.id}`\n"
        f"👤 **Username:** @{target.username if target.username else 'N/A'}\n"
        f"🤖 **Is Bot:** {'Yes' if target.is_bot else 'No'}\n"
        f"🔗 **User Link:** [Link](tg://user?id={target.id})\n"
    )
    
    # Try to get profile photos
    photos = await message.bot.get_user_profile_photos(target.id, limit=1)
    if photos.total_count > 0:
        await message.reply_photo(photo=photos.photos[0][-1].file_id, caption=info, parse_mode="Markdown")
    else:
        await message.reply(info, parse_mode="Markdown")

# --- 🌍 IP INVESTIGATOR ---
@router.message(Command("ip"))
async def ip_lookup(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❓ Please provide an IP address.\nExample: `/ip 8.8.8.8`", parse_mode="Markdown")

    ip = args[1]
    url = f"http://ip-api.com/json/{ip}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data.get("status") == "fail":
                return await message.reply(f"❌ Error: {data.get('message')}")

            info = (
                f"🌐 **IP Investigation: {ip}**\n\n"
                f"📍 **Country:** {data.get('country')} ({data.get('countryCode')})\n"
                f"🏙️ **City:** {data.get('city')}\n"
                f"🏢 **ISP:** {data.get('isp')}\n"
                f"📡 **Org:** {data.get('org')}\n"
                f"🗺️ **Coords:** `{data.get('lat')}, {data.get('lon')}`"
            )
            await message.reply(info, parse_mode="Markdown")

# --- 🐙 GITHUB LOOKUP ---
@router.message(Command("github"))
async def github_lookup(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❓ Provide a GitHub username.")

    username = args[1]
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/users/{username}") as response:
            if response.status != 200:
                return await message.reply("❌ GitHub user not found.")
            user = await response.json()
            
            info = (
                f"👤 **GitHub:** {user.get('name') or username}\n"
                f"📝 **Bio:** {user.get('bio') or 'N/A'}\n"
                f"📁 **Repos:** `{user.get('public_repos')}`\n"
                f"👥 **Followers:** `{user.get('followers')}`\n"
                f"🔗 [Profile]({user.get('html_url')})"
            )
            await message.reply(info, parse_mode="Markdown")
