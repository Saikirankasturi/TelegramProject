import asyncio
from bot import create_bot_app
from forwarder import start_forwarder

# Start Google Sheets bot
app = create_bot_app()
asyncio.create_task(app.start())  # Initialize the bot
asyncio.create_task(app.updater.start_polling())  # Start polling
print("Sheets bot running...")

# Start forwarder
asyncio.create_task(start_forwarder())
print("Forwarder task started...")

# Keep loop alive
asyncio.get_event_loop().run_forever()