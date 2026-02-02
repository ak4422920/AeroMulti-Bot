import os
from aiogram import BaseMiddleware, types
from typing import Callable, Dict, Any, Awaitable
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ForceSubMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any]
    ) -> Any:
        # Ignore non-message events or service messages
        if not isinstance(event, types.Message) or not event.from_user:
            return await handler(event, data)

        # Skip check for admins or if it's a private chat check
        bot = data['bot']
        channel_id = os.getenv("AUTH_CHANNEL_ID")
        channel_link = os.getenv("AUTH_CHANNEL_LINK")

        if not channel_id:
            return await handler(event, data)

        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=event.from_user.id)
            if member.status in ["member", "administrator", "creator"]:
                return await handler(event, data)
        except Exception:
            pass # Usually happens if bot isn't admin in channel

        # If not subscribed, show join message
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📢 Join Channel", url=channel_link))
        
        return await event.answer(
            "❌ **Access Denied!**\n\nYou must join our channel to use this bot.",
            reply_markup=builder.as_markup()
        )
