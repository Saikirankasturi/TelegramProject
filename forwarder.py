import os
from telethon import TelegramClient, events

async def start_forwarder():
    api_id = int(os.environ.get("API_ID"))
    api_hash = os.environ.get("API_HASH")
    SOURCE_GROUP_ID = int(os.environ.get("SOURCE_GROUP_ID"))
    DEST_GROUP_ID = int(os.environ.get("DEST_GROUP_ID"))

    client = TelegramClient('session', api_id, api_hash)

    @client.on(events.NewMessage(chats=SOURCE_GROUP_ID))
    async def forward_to_group(event):
        await client.forward_messages(
            entity=DEST_GROUP_ID,
            messages=event.message,
            from_peer=SOURCE_GROUP_ID
        )
        print(f"Forwarded message: {event.message.text}")

    await client.start()
    print("Forwarder running...")
    await client.run_until_disconnected()