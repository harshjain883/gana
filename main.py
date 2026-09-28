import os
import uuid
from fastapi import FastAPI, HTTPException, Header, Depends
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = FastAPI(title="Spotify Music Bridge API")

# In-memory database for keys
API_KEYS_DB = {}

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Welcome to Spotify Music API Generator Bot!**\n\n"
        "Commands:\n"
        "🔑 `/generate` - Get your permanent Spotify API Key and Server URL.\n"
        "ℹ️ `/help` - How to use this with your Music Bot."
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
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
    await update.message.reply_text(response_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **How to link with your Music Bot:**\n"
        "1. Use `/generate` to get your key and URL.\n"
        "2. Set `SPOTIFY_API_KEY` and `SPOTIFY_API_URL` in your music bot.\n"
        "3. Your music bot will now stream restriction-free songs!"
    )

# FastAPI Endpoints
def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in API_KEYS_DB:
        raise HTTPException(status_code=403, detail="Invalid or Missing Permanent Spotify API Key")
    return x_api_key

@app.get("/")
async def root():
    return {"status": "Active", "system": "Spotify Music InnerTube Bridge API"}

@app.get("/stream")
async def get_stream_url(query: str, api_key: str = Depends(verify_api_key)):
    return {
        "status": "success",
        "query": query,
        "stream_url": "https://www.youtube.com/watch?v=sample_stream_link",
        "provider": "Spotify Music Engine"
    }

if __name__ == "__main__":
    import uvicorn
    import threading

    # Telegram Bot runner using python-telegram-bot
    def run_telegram_bot():
        if not BOT_TOKEN:
            print("❌ Error: BOT_TOKEN environment variable is missing!")
            return
        
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("generate", generate))
        application.add_handler(CommandHandler("help", help_command))
        
        print("🤖 Telegram Bot Polling Started...")
        application.run_polling()

    # Start bot in a background thread
    threading.Thread(target=run_telegram_bot, daemon=True).start()

    # Run FastAPI server
    print("🚀 Starting FastAPI Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
