import os
from datetime import datetime

async def send_log(bot, message, action):
    log_chat_id = os.getenv("LOG_CHANNEL_ID")
    if not log_chat_id:
        return
    
    user = message.from_user
    log_text = (
        f"📢 **New Bot Activity**\n\n"
        f"👤 **User:** {user.full_name} (@{user.username})\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🛠️ **Action:** `{action}`\n"
        f"📅 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    try:
        await bot.send_message(chat_id=log_chat_id, text=log_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Log Error: {e}")
