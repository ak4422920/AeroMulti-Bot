import random
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReactionTypeEmoji
from database import groups_col  # Importing our MongoDB collection

router = Router()

# List of emojis to choose from
REACTION_EMOJIS = ["👍", "❤️", "🔥", "🥰", "👏", "🤩", "⚡", "🎉"]

# --- ⚙️ TOGGLE AUTO-REACTION ---
@router.message(Command("autoreaction"))
async def toggle_reaction(message: types.Message):
    # Check if user is admin
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        return await message.reply("❌ Only admins can use this command!")

    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Usage: `/autoreaction on` or `/autoreaction off`", parse_mode="Markdown")

    status = args[1].lower()
    chat_id = message.chat.id

    if status == "on":
        await groups_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"auto_reaction": True}},
            upsert=True
        )
        await message.reply("✅ Auto-Reaction enabled for this group!")
    elif status == "off":
        await groups_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"auto_reaction": False}},
            upsert=True
        )
        await message.reply("❌ Auto-Reaction disabled.")

# --- ❤️ THE AUTO-REACTION LOGIC ---
@router.message(F.chat.type.in_({"group", "supergroup"}))
async def auto_react_handler(message: types.Message):
    # Check MongoDB to see if this group has the feature ON
    group_data = await groups_col.find_one({"chat_id": message.chat.id})
    
    if group_data and group_data.get("auto_reaction"):
        try:
            # Select a random emoji
            emoji = random.choice(REACTION_EMOJIS)
            # Set the reaction (aiogram 3.x style)
            await message.react([ReactionTypeEmoji(emoji=emoji)])
        except Exception:
            pass # Ignore errors if bot lacks permissions
