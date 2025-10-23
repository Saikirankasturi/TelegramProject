import asyncio
from bot import create_bot_app
from forwarder import start_forwarder

async def main():
    # Start Sheets bot
    app = create_bot_app()
    await app.initialize()  # initialize the app
    asyncio.create_task(app.start_polling())  # polling runs in background
    print("Sheets bot running...")

    # Start forwarder
    asyncio.create_task(start_forwarder())
    print("Forwarder task started...")

    # Keep the program running
    while True:
        await asyncio.sleep(60)

# Run the main coroutine
asyncio.run(main())
