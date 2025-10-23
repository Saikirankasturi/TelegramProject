# forwarder.py
from telethon import TelegramClient, events

# --- TELEGRAM API CREDENTIALS ---
api_id = 27492786         # from my.telegram.org
api_hash = '74b85df0a8bff63886d44486af99b8ac'

# --- GROUP IDS ---
SOURCE_GROUP_ID = -4932715397   # Original private group
DEST_GROUP_ID = -1003014043009  # New group where bot is added

# --- CLIENT SETUP ---
client = TelegramClient('session', api_id, api_hash)

# --- EVENT HANDLER ---
@client.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def forward_to_group(event):
    # Forward the message as-is
    await client.forward_messages(
        entity=DEST_GROUP_ID,
        messages=event.message,
        from_peer=SOURCE_GROUP_ID
    )
    print(f"Forwarded message with original metadata: {event.message.text}")

# --- RUN CLIENT ---
print("Forwarding script running...")
client.start()
client.run_until_disconnected()