import os
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ForceSubMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, types.Message) or not event.from_user or event.chat.type != "private":
            return await handler(event, data)

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
            pass 

        # FIXED: Using proper InlineKeyboardButton with URL
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 Join Channel", url=f"{channel_link}")
        
        return await event.answer(
            "⚠️ **Access Denied!**\n\nYou must join our updates channel to use this bot.",
            reply_markup=builder.as_markup()
        )
