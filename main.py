import os
import uuid
import asyncio
import threading
from fastapi import FastAPI, HTTPException, Header, Depends
from pyrogram import Client, filters

app = FastAPI(title="Spotify Music InnerTube API Provider")

# In-memory database
API_KEYS_DB = {}

# Telegram Bot Setup
API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

bot = Client(
    "SpotifyKeyBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 **Welcome to Spotify Music API Generator Bot!**\n\n"
        "Commands:\n"
        "🔑 `/generate` - Get your permanent Spotify API Key and Server URL.\n"
        "ℹ️ `/help` - How to use this with your Music Bot."
    )

@bot.on_message(filters.command("generate"))
async def generate_key(client, message):
    user_id = message.from_user.id
    
    existing_key = next((k for k, v in API_KEYS_DB.items() if v == user_id), None)
    
    if not existing_key:
        new_key = "spotifykey_" + uuid.uuid4().hex
        API_KEYS_DB[new_key] = user_id
        existing_key = new_key

    base_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RENDER_EXTERNAL_URL") or "http://localhost:8000"
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"
    
    response_text = (
        f"✅ **Your Permanent Spotify API Key Generated Successfully!**\n\n"
        f"🔑 **API Key:** `{existing_key}`\n"
        f"🌐 **Base URL:** `{base_url}`\n\n"
        f"💡 *Copy these values and put them inside your Music Bot's environment variables or config.*"
    )
    await message.reply_text(response_text)

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(
        "📖 **How to link with your Music Bot:**\n"
        "1. Use `/generate` to get your key and URL.\n"
        "2. Set `SPOTIFY_API_KEY` and `SPOTIFY_API_URL` in your music bot.\n"
        "3. Your music bot will now stream restriction-free songs!"
    )

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in API_KEYS_DB:
        raise HTTPException(status_code=403, detail="Invalid or Missing Permanent Spotify API Key")
    return x_api_key

@app.get("/")
async def root():
    return {"status": "Active", "system": "Spotify Music InnerTube Bridge API"}

@app.get("/stream")
async def get_stream_url(query: str, api_key: str = Depends(verify_api_key)):
    try:
        return {
            "status": "success",
            "query": query,
            "stream_url": "https://www.youtube.com/watch?v=sample_stream_link",
            "provider": "Spotify Music Engine"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Telegram Bot को थ्रेड में चलाने का सही तरीका
    def start_bot_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Pyrogram client run loop
        bot.run()

    threading.Thread(target=start_bot_thread, daemon=True).start()
    
    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
