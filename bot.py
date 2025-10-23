# bot_forwarder_combined.py
import os
import json
import re
import gspread
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from google.oauth2.service_account import Credentials
from telethon import TelegramClient, events

# --- CONFIG BOT ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")
TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID", 0))
GOOGLE_CREDS = os.environ.get("GOOGLE_CREDS")

if not BOT_TOKEN or not SHEET_ID or not GOOGLE_CREDS:
    raise ValueError("BOT_TOKEN, SHEET_ID, or GOOGLE_CREDS missing!")

# --- CONFIG FORWARDER ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")
SOURCE_GROUP_ID = int(os.environ.get("SOURCE_GROUP_ID", 0))
DEST_GROUP_ID = int(os.environ.get("DEST_GROUP_ID", 0))

if not API_ID or not API_HASH or not SOURCE_GROUP_ID or not DEST_GROUP_ID:
    raise ValueError("Telethon API_ID, API_HASH or GROUP IDs missing!")

# --- Google Sheets setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_info(json.loads(GOOGLE_CREDS), scopes=SCOPES)
client_gs = gspread.authorize(CREDS)
sheet = client_gs.open_by_key(SHEET_ID).sheet1
header = ["Timestamp", "Symbol", "Timeframe", "Move Type", "Direction", "Price", "Forwarded"]
try:
    if sheet.row_values(1) != header:
        sheet.insert_row(header, index=1)
except gspread.exceptions.APIError:
    sheet.insert_row(header, index=1)

# --- Regex pattern ---
pattern = re.compile(
    r'(?P<symbol>\w+)\s*-\s*(?P<timeframe>\w+)\s*'
    r'(?P<move_type>Normal|Bigger)\s*'
    r'(?P<direction>upper|lower|Upper|Lower)?\s*'
    r'move hit\s*(?P<price>[\d\.]+)',
    re.IGNORECASE
)

# --- TELEGRAM BOT HANDLERS ---
async def log_stock_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = update.message.text or update.message.caption or ""
    if not text.strip():
        return
    is_forwarded = any([
        getattr(update.message, "forward_from", None),
        getattr(update.message, "forward_from_chat", None),
        getattr(update.message, "forward_date", None)
    ])
    chat_id = update.message.chat.id
    if TARGET_CHAT_ID and chat_id != TARGET_CHAT_ID:
        return
    matches = list(pattern.finditer(text))
    if not matches:
        return
    for match in matches:
        data = match.groupdict()
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            timestamp,
            data["symbol"].upper(),
            data["timeframe"],
            data["move_type"],
            (data.get("direction") or "").capitalize(),
            data["price"],
            "Yes" if is_forwarded else "No",
        ]
        try:
            sheet.append_row(row)
            print(f"[SUCCESS] Logged: {row}")
        except Exception as e:
            print(f"[ERROR] Failed to append: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sheets bot is running...")

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.message.chat.id}")

# --- TELETHON FORWARDER ---
client_tele = TelegramClient("session", API_ID, API_HASH)

@client_tele.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def forward_to_group(event):
    await client_tele.forward_messages(
        entity=DEST_GROUP_ID,
        messages=event.message,
        from_peer=SOURCE_GROUP_ID
    )
    print(f"[Forwarder] Forwarded message: {event.message.text}")

# --- MAIN FUNCTION ---
async def main():
    # Start BOT
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("getid", get_chat_id))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, log_stock_message))
    print("🚀 Sheets bot running...")
    
    # Start Telethon forwarder
    await client_tele.start()
    print("🚀 Forwarder running...")

    # Run both concurrently
    await asyncio.gather(
        app.run_polling(),
        client_tele.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())