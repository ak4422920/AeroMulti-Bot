from aiogram import Router, types, F
from aiogram.filters import Command
from database import groups_col
from datetime import datetime
import asyncio

router = Router()

@router.message(Command("nightmode"))
async def set_night_mode(message: types.Message):
    # Check if user is admin
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        return await message.reply("❌ Only admins can set Night Mode!")

    args = message.text.split()
    if len(args) < 3:
        return await message.reply(
            "📋 **Usage:** `/nightmode [close_hour] [open_hour]`\n"
            "Example: `/nightmode 0 6` (Closes at 12 AM, Opens at 6 AM)",
            parse_mode="Markdown"
        )

    try:
        close_h = int(args[1])
        open_h = int(args[2])
        
        await groups_col.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"night_mode": True, "close_h": close_h, "open_h": open_h}},
            upsert=True
        )
        await message.reply(f"🌙 **Night Mode Configured!**\nGroup will mute at `{close_h}:00` and unmute at `{open_h}:00` daily.")
    except ValueError:
        await message.reply("❌ Please use numbers only (0-23).")

# This is the "Guard" that checks every message
@router.message(F.chat.type.in_({"group", "supergroup"}))
async def night_guard(message: types.Message):
    group_data = await groups_col.find_one({"chat_id": message.chat.id})
    if not group_data or not group_data.get("night_mode"):
        return

    # Check current hour
    now = datetime.now().hour
    close_h = group_data.get("close_h")
    open_h = group_data.get("open_h")

    # Check if we are inside the "Silent" window
    is_night = False
    if close_h < open_h:
        is_night = close_h <= now < open_h
    else: # Handles overnight (e.g., 22:00 to 06:00)
        is_night = now >= close_h or now < open_h

    if is_night:
        # Check if sender is an admin
        member = await message.chat.get_member(message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            try:
                await message.delete()
            except:
                pass # Bot might not have delete permissions
