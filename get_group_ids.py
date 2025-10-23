from telethon import TelegramClient

# Replace with your Telegram API credentials
api_id = 27492786
api_hash = '74b85df0a8bff63886d44486af99b8ac'

client = TelegramClient('session', api_id, api_hash)

async def main():
    async for dialog in client.iter_dialogs():
        print(f"{dialog.name} -> ID: {dialog.id}")

with client:
    client.loop.run_until_complete(main())
