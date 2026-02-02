import uuid
from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link
from database import files_col # Ensure this is in your database.py

router = Router()

# --- 📥 SAVE FILE & GENERATE LINK ---
@router.message(F.document | F.video | F.audio | F.photo)
async def handle_file_upload(message: types.Message, bot):
    # Determine the file_id and type
    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.photo:
        file_id = message.photo[-1].file_id # Get highest quality
        file_type = "photo"

    # Generate a unique short code for the link
    short_id = str(uuid.uuid4())[:8]

    # Save to MongoDB
    await files_col.insert_one({
        "short_id": short_id,
        "file_id": file_id,
        "file_type": file_type,
        "uploader": message.from_user.id
    })

    # Create the Deep Link (t.me/bot?start=short_id)
    share_link = await create_start_link(bot, short_id, encode=True)
    
    await message.reply(
        f"✅ **File Stored!**\n\n"
        f"Anyone with this link can download it:\n"
        f"🔗 `{share_link}`",
        parse_mode="Markdown"
    )

# --- 📤 DELIVER FILE VIA DEEP LINK ---
@router.message(CommandStart(deep_link=True))
async def handler(message: types.Message, command: CommandObject):
    # The payload is the short_id we encoded earlier
    from aiogram.utils.deep_linking import decode_payload
    payload = decode_payload(command.args)

    # Find file in MongoDB
    file_data = await files_col.find_one({"short_id": payload})

    if not file_data:
        return await message.answer("❌ This file link has expired or is invalid.")

    file_id = file_data['file_id']
    f_type = file_data['file_type']

    # Send the correct type back to the user
    if f_type == "document":
        await message.answer_document(file_id)
    elif f_type == "video":
        await message.answer_video(file_id)
    elif f_type == "audio":
        await message.answer_audio(file_id)
    elif f_type == "photo":
        await message.answer_photo(file_id)
