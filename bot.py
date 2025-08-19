import os
from pyrogram import Client, filters
from guessit import guessit
from pymediainfo import MediaInfo

API_ID = int(os.getenv("API_ID", "25259066"))
API_HASH = os.getenv("API_HASH", "caad2cdad2fe06057f2bf8f8a8e58950")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7859842889:AAG5jD89VW5xEo9qXT8J0OsB-byL5aJTqZM")

app = Client("caption_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# --- Extract metadata ---
def extract_metadata(file_path: str, file_name: str):
    # Parse from filename
    parsed = guessit(file_name)
    title = parsed.get("title", "Unknown")
    year = parsed.get("year", "")

    # Parse from metadata
    media_info = MediaInfo.parse(file_path)

    resolution = ""
    audio_langs = []

    for track in media_info.tracks:
        if track.track_type == "Video":
            if track.height:
                resolution = f"{track.height}p"
        elif track.track_type == "Audio":
            if track.language:
                audio_langs.append(track.language.capitalize())

    audio = " ".join(sorted(set(audio_langs))) if audio_langs else "Unknown"

    caption = f"{title} ({year}) {audio} {resolution}.mkv".strip()
    return caption


# --- Handle new media ---
@app.on_message(filters.document | filters.video)
async def caption_handler(client, message):
    file = message.document or message.video
    file_name = file.file_name

    # Download temporarily to read metadata
    temp_file = await message.download()

    # Extract caption
    caption = extract_metadata(temp_file, file_name)

    # Clean up temp file
    os.remove(temp_file)

    # Edit the original message caption
    try:
        await message.edit_caption(caption)
    except Exception as e:
        await message.reply_text(f"❌ Failed to edit caption: {e}")


print("✅ Bot is running...")
app.run()
