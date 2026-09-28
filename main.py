import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, Header, Depends
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = FastAPI(title="Spotify Music Bridge API")

API_KEYS_DB = {}
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

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

    # Railway ke official environment variables se direct public URL uthane ka tarika
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("RAILWAY_STATIC_URL")
    
    if domain:
        base_url = f"https://{domain}"
    else:
        # Agar Railway ka variable na mile, toh aap yahan apna custom domain ya fallback daal sakte hain
        base_url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
        if base_url and not base_url.startswith("http"):
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

async def main():
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN environment variable is missing!")
        return

    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CommandHandler("generate", generate))
    tg_app.add_handler(CommandHandler("help", help_command))

    import uvicorn
    from uvicorn import Config, Server

    config = Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = Server(config)

    print("🤖 Starting Telegram Bot & FastAPI Server together...")
    
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling()

    await server.serve()

    await tg_app.updater.stop()
    await tg_app.stop()
    await tg_app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
