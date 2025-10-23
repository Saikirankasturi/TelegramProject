# forwarder.py
import asyncio
import os
from telethon import TelegramClient, events

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")
SOURCE_GROUP_ID = int(os.environ.get("SOURCE_GROUP_ID", 0))
DEST_GROUP_ID = int(os.environ.get("DEST_GROUP_ID", 0))

if not API_ID or not API_HASH or not SOURCE_GROUP_ID or not DEST_GROUP_ID:
    raise ValueError("Telethon API_ID, API_HASH or GROUP IDs missing!")

client = TelegramClient("session", API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def forward_to_group(event):
    await client.forward_messages(
        entity=DEST_GROUP_ID,
        messages=event.message,
        from_peer=SOURCE_GROUP_ID
    )
    print(f"Forwarded message: {event.message.text}")

async def main():
    print("🚀 Forwarder running...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
