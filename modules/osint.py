import aiohttp
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("github"))
async def github_lookup(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❓ Please provide a GitHub username.\nExample: `/github torvalds`", parse_mode="Markdown")

    username = args[1]
    url = f"https://api.github.com/users/{username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return await message.reply("❌ User not found on GitHub.")
            
            data = await response.text()
            import json
            user = json.loads(data)

            info = (
                f"👤 **GitHub Profile: {user.get('name') or username}**\n\n"
                f"📝 **Bio:** {user.get('bio') or 'No bio'}\n"
                f"📁 **Public Repos:** `{user.get('public_repos')}`\n"
                f"👥 **Followers:** `{user.get('followers')}` | **Following:** `{user.get('following')}`\n"
                f"📍 **Location:** {user.get('location') or 'Global'}\n\n"
                f"🔗 [Open Profile]({user.get('html_url')})"
            )
            
            if user.get('avatar_url'):
                await message.reply_photo(photo=user.get('avatar_url'), caption=info, parse_mode="Markdown")
            else:
                await message.reply(info, parse_mode="Markdown")

@router.message(Command("insta"))
async def insta_lookup(message: types.Message):
    # Instagram is strict, so we use a public viewer link as a workaround
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❓ Please provide an Instagram username.\nExample: `/insta nasa`")

    username = args[1].replace("@", "")
    info = (
        f"📸 **Instagram Lookup: @{username}**\n\n"
        f"Due to Instagram's privacy settings, I can't pull direct data, but you can view the profile here:\n"
        f"🔗 [View Profile](https://www.instagram.com/{username}/)\n"
        f"🔗 [View Anonymously](https://imginn.com/user/{username}/)"
    )
    await message.reply(info, parse_mode="Markdown", disable_web_page_preview=False)
