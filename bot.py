# bot.py
import os
import gspread
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from google.oauth2.service_account import Credentials
import re
import json
import os
from google.oauth2.service_account import Credentials


# --- CONFIG ---
try:
    from config import BOT_TOKEN, SHEET_ID, TARGET_CHAT_ID
except ImportError:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    SHEET_ID = os.environ.get("SHEET_ID")
    TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID", 0))

if not BOT_TOKEN or not SHEET_ID:
    raise ValueError("BOT_TOKEN or SHEET_ID is missing!")

print(f"[DEBUG] TARGET_CHAT_ID={TARGET_CHAT_ID}")

# --- Google Sheets setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds_json = os.environ.get("GOOGLE_CREDS")
if not creds_json:
    raise ValueError("GOOGLE_CREDS environment variable is missing!")

CREDS = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
client = gspread.authorize(CREDS)
sheet = client.open_by_key(SHEET_ID).sheet1

print(f"[DEBUG] Sheet title: {sheet.title}, Current rows: {len(sheet.get_all_values())}")

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

# --- Handlers ---
async def log_stock_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    # Handle both plain text and photo with caption
    text = update.message.text or update.message.caption or ""
    if not text.strip():
        return

    # Check if message was forwarded
    is_forwarded = any([
        getattr(update.message, "forward_from", None),
        getattr(update.message, "forward_from_chat", None),
        getattr(update.message, "forward_date", None)
    ])

    chat_id = update.message.chat.id
    print(f"[DEBUG] Received message from chat {chat_id} | Forwarded: {is_forwarded}")
    print(f"[DEBUG] Message text:\n{text}")

    # Only log from your target chat
    if TARGET_CHAT_ID and chat_id != TARGET_CHAT_ID:
        print(f"[DEBUG] Skipping chat {chat_id} (TARGET_CHAT_ID={TARGET_CHAT_ID})")
        return

    # Find all matches (handles multi-line text)
    matches = list(pattern.finditer(text))
    if not matches:
        print(f"[DEBUG] Regex did NOT match any alerts: '{text}'")
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
            print(f"[SUCCESS] Logged stock alert: {row}")
        except Exception as e:
            print(f"[ERROR] Failed to append row: {e}")

# --- Commands ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 🤖 Stock Alert Bot is running.\n"
        "Messages (including forwarded ones and image captions) will be logged to Google Sheets."
    )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.message.chat.id}")

# --- Bot App ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("getid", get_chat_id))
# Handle both text and photo messages
app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, log_stock_message))

print("🚀 Stock alert bot is running...")
app.run_polling()
