import asyncio
from bot import create_bot_app
from forwarder import start_forwarder

# Start Google Sheets bot
app = create_bot_app()
app.start()          # Initializes the bot
app.updater.start_polling()  # Starts polling in the background
print("Sheets bot running...")

# Start Telethon forwarder
async def main():
    await start_forwarder()

loop = asyncio.get_event_loop()
loop.create_task(main())
print("Forwarder task started...")
loop.run_forever()
