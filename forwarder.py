from telethon import TelegramClient, events
import config  # Import sensitive info

# --- CLIENT SETUP ---
client = TelegramClient('session', config.API_ID, config.API_HASH)

# --- EVENT HANDLER ---
@client.on(events.NewMessage(chats=config.SOURCE_GROUP_ID))
async def forward_to_group(event):
    await client.forward_messages(
        entity=config.DEST_GROUP_ID,
        messages=event.message,
        from_peer=config.SOURCE_GROUP_ID
    )
    print(f"Forwarded message: {event.message.text}")

# --- RUN CLIENT ---
print("Forwarding script running...")
client.start()
client.run_until_disconnected()