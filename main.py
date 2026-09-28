import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, Header, Depends
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

app = FastAPI(title="Spotify Music Bridge API")

API_KEYS_DB = {}
# Mock usage database for demo (user_id: {"requests": 19, "audio": 17, "video": 2, "total": 202})
USER_USAGE = {}

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Main Menu / Panel Keyboard
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔑 Get API Key", callback_data="get_key")],
        [InlineKeyboardButton("📊 Check Usage", callback_data="check_usage")],
        [InlineKeyboardButton("ℹ️ Help & Info", callback_data="help_info")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎵 **Spotify Music API Dashboard**\n\n"
        "Welcome! Use the buttons below to manage your API key and check your usage instantly."
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data

    if data == "get_key":
        existing_key = next((k for k, v in API_KEYS_DB.items() if v == user_id), None)
        if not existing_key:
            # Short and clean key format
            new_key = "sb_" + uuid.uuid4().hex[:16]
            API_KEYS_DB[new_key] = user_id
            existing_key = new_key

        base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("RAILWAY_STATIC_URL") or "http://localhost:8000"
        if base_url and not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        key_text = (
            f"✅ **Your API Key Details**\n\n"
            f"🔑 **Key:** `{existing_key}`\n"
            f"🟢 **Status:** `Active`\n"
            f"🌐 **URL:** `{base_url}`\n\n"
            f"*(Copy this and paste it into your music bot config)*"
        )
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]])
        await query.edit_message_text(key_text, reply_markup=back_keyboard, parse_mode="Markdown")

    elif data == "check_usage":
        # Fetch or mock usage stats
        stats = USER_USAGE.get(user_id, {"req": 19, "audio": 17, "video": 2, "total": 202})
        
        usage_text = (
            f"📊 **Your API Usage Stats**\n\n"
            f"🟢 **Status:** `Active`\n\n"
            f"📅 **Today's Usage:**\n"
            f" • Requests: `{stats['req']}`\n"
            f" • Audio: `{stats['audio']}`\n"
            f" • Video: `{stats['video']}`\n\n"
            f"📈 **All-Time Usage:**\n"
            f" • Total Requests: `{stats['total']}`"
        )
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]])
        await query.edit_message_text(usage_text, reply_markup=back_keyboard, parse_mode="Markdown")

    elif data == "help_info":
        help_text = (
            "📖 **Quick Guide:**\n\n"
            "1. Click **Get API Key** to generate your small, clean permanent key & URL.\n"
            "2. Click **Check Usage** to view your live request stats.\n"
            "3. Put them in your music bot to stream songs smoothly!"
        )
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]])
        await query.edit_message_text(help_text, reply_markup=back_keyboard, parse_mode="Markdown")

    elif data == "main_menu":
        await start(update, context)

# FastAPI Endpoints
def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in API_KEYS_DB:
        raise HTTPException(status_code=403, detail="Invalid API Key")
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
        print("❌ Error: BOT_TOKEN is missing!")
        return

    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(button_handler))

    import uvicorn
    from uvicorn import Config, Server

    config = Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = Server(config)

    print("🤖 Starting Bot with Buttons & FastAPI...")
    
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling()

    await server.serve()

    await tg_app.updater.stop()
    await tg_app.stop()
    await tg_app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
