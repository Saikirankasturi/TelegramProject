import os
from telethon import TelegramClient, events

async def start_forwarder():
    bot_token = os.environ.get("BOT_TOKEN")
    api_id = int(os.environ.get("API_ID"))
    api_hash = os.environ.get("API_HASH")
    source_id = int(os.environ.get("SOURCE_GROUP_ID"))
    dest_id = int(os.environ.get("DEST_GROUP_ID"))

    # Login using bot token (no phone required)
    client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

    @client.on(events.NewMessage(chats=source_id))
    async def forward(event):
        print(f"[DEBUG] Got message: {event.message.text}")
        await client.forward_messages(dest_id, event.message, from_peer=source_id)
        print(f"[SUCCESS] Forwarded message")

    print("Forwarder running...")
    await client.run_until_disconnected()