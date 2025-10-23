# forwarder.py
import asyncio
import os
from telethon import TelegramClient, events

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Bot token for Telethon
SOURCE_GROUP_ID = int(os.environ.get("SOURCE_GROUP_ID", 0))
DEST_GROUP_ID = int(os.environ.get("DEST_GROUP_ID", 0))

if not API_ID or not API_HASH or not BOT_TOKEN or not SOURCE_GROUP_ID or not DEST_GROUP_ID:
    raise ValueError("Missing Telethon configuration!")

# Use bot token to avoid interactive phone login
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def forward_to_group(event):
    try:
        await client.forward_messages(
            entity=DEST_GROUP_ID,
            messages=event.message,
            from_peer=SOURCE_GROUP_ID
        )
        print(f"Forwarded message: {event.message.text}")
    except Exception as e:
        print(f"[ERROR] Could not forward message: {e}")

async def main():
    print("🚀 Forwarder running...")
    # client.start() is not needed, already started with bot_token
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())