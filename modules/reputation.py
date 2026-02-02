from aiogram import Router, types, F
from aiogram.filters import Command
from database import users_col

router = Router()

# Expanded dictionary of praise and karma triggers
KARMA_KEYWORDS = [
    "+1", "thanks", "thank you", "ty", "thx", "good bot", "helpful",
    "w", "goat", "clutch", "based", "legend", "nice one", "well done",
    "🌟", "✅", "🔥", "🙌", "⭐", "🔝"
]

@router.message(F.reply_to_message)
async def add_karma(message: types.Message):
    # Check if message is just the keyword or contains it
    text = message.text.lower() if message.text else ""
    if not any(word in text for word in KARMA_KEYWORDS):
        return

    reply_to = message.reply_to_message
    
    # Validation
    if reply_to.from_user.id == message.from_user.id:
        return await message.reply("❌ You can't give karma to yourself!")

    if reply_to.from_user.is_bot:
        return

    # Update MongoDB
    await users_col.update_one(
        {"user_id": reply_to.from_user.id},
        {"$inc": {"karma": 1}, "$set": {"username": reply_to.from_user.first_name}},
        upsert=True
    )

    user_data = await users_col.find_one({"user_id": reply_to.from_user.id})
    new_karma = user_data.get("karma", 0)

    # Fun response based on the point total
    response = f"🌟 **{reply_to.from_user.first_name}** earned a point!"
    if new_karma % 10 == 0:
        response += f"\n🔥 Wow! They hit a milestone of `{new_karma}` points!"
    else:
        response += f" (Total: `{new_karma}`)"

    await message.answer(response)

@router.message(Command("top"))
async def get_leaderboard(message: types.Message):
    cursor = users_col.find({"karma": {"$exists": True}}).sort("karma", -1).limit(10)
    top_users = await cursor.to_list(length=10)

    if not top_users:
        return await message.reply("🏆 No karma points awarded yet!")

    leaderboard = "🏆 **AeroMulti Karma Leaders** 🏆\n\n"
    for i, user in enumerate(top_users, 1):
        name = user.get("username", "Unknown")
        pts = user.get("karma", 0)
        # Add medals for top 3
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard += f"{medal} {name} — `{pts} pts`\n"

    await message.reply(leaderboard, parse_mode="Markdown")
