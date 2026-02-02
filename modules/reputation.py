from aiogram import Router, types, F
from aiogram.filters import Command
from database import users_col # We use our existing MongoDB collection

router = Router()

# Keywords that trigger a Karma increase
KARMA_KEYWORDS = ["+1", "thanks", "thank you", "good bot", "helpful"]

@router.message(F.reply_to_message)
async def add_karma(message: types.Message):
    # Check if the message contains a keyword
    if not any(word in message.text.lower() for word in KARMA_KEYWORDS):
        return

    # Basic Rules
    reply_to = message.reply_to_message
    
    # 1. Don't give karma to yourself
    if reply_to.from_user.id == message.from_user.id:
        return await message.reply("❌ You can't give karma to yourself, nice try!")

    # 2. Don't give karma to bots
    if reply_to.from_user.is_bot:
        return

    # Update MongoDB: Increment points by 1
    # upsert=True creates the user if they don't exist yet
    await users_col.update_one(
        {"user_id": reply_to.from_user.id},
        {"$inc": {"karma": 1}, "$set": {"username": reply_to.from_user.first_name}},
        upsert=True
    )

    # Get the new total to show the user
    user_data = await users_col.find_one({"user_id": reply_to.from_user.id})
    new_karma = user_data.get("karma", 0)

    await message.answer(
        f"🌟 **{reply_to.from_user.first_name}** earned a point!\n"
        f"Total Karma: `{new_karma}`"
    )

@router.message(Command("top"))
async def get_leaderboard(message: types.Message):
    # Fetch top 10 users sorted by karma
    cursor = users_col.find().sort("karma", -1).limit(10)
    top_users = await cursor.to_list(length=10)

    if not top_users:
        return await message.reply("🏆 No karma points awarded yet!")

    leaderboard = "🏆 **Karma Leaderboard** 🏆\n\n"
    for i, user in enumerate(top_users, 1):
        name = user.get("username", "Unknown")
        pts = user.get("karma", 0)
        leaderboard += f"{i}. {name} — `{pts} pts`\n"

    await message.reply(leaderboard, parse_mode="Markdown")
