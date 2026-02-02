from aiogram import Router, types, F
from aiogram.filters import Command
from database import users_col
import time

router = Router()

@router.message(Command("afk"))
async def set_afk(message: types.Message):
    reason = message.text.replace("/afk", "").strip() or "Away"
    user_id = message.from_user.id
    
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"afk": True, "afk_reason": reason, "afk_time": time.time()}},
        upsert=True
    )
    
    await message.reply(f"💤 **{message.from_user.first_name}** is now AFK: `{reason}`")

@router.message()
async def check_afk(message: types.Message):
    if not message.from_user or message.from_user.is_bot:
        return

    # 1. Check if the user sending the message was AFK (Remove AFK status)
    user_data = await users_col.find_one({"user_id": message.from_user.id})
    if user_data and user_data.get("afk"):
        await users_col.update_one({"user_id": message.from_user.id}, {"$set": {"afk": False}})
        await message.reply(f"👋 Welcome back **{message.from_user.first_name}**! I've removed your AFK.")

    # 2. Check if the message mentions someone who is AFK
    if message.entities:
        for entity in message.entities:
            # Handle @mentions and text_mentions
            target_id = None
            if entity.type == "mention":
                # Mentions require searching username in DB (optional complexity)
                pass 
            elif entity.type == "text_mention":
                target_id = entity.user.id
            
            # Simplified: Check if it's a reply to someone
            if message.reply_to_message:
                target_id = message.reply_to_message.from_user.id
            
            if target_id:
                target_data = await users_col.find_one({"user_id": target_id})
                if target_data and target_data.get("afk"):
                    reason = target_data.get("afk_reason")
                    await message.reply(f"🚫 This user is AFK: `{reason}`")
                  
