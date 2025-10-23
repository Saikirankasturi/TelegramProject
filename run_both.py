import asyncio
from bot import create_bot_app
from forwarder import start_forwarder

async def start_bot():
    app = create_bot_app()
    print("Bot running...")
    await app.run_polling()

async def main():
    # Run both bots concurrently
    bot_task = asyncio.create_task(start_bot())
    forwarder_task = asyncio.create_task(start_forwarder())
    
    # Keep the program running while both tasks are active
    await asyncio.gather(bot_task, forwarder_task)

if __name__ == "__main__":
    print("🚀 Running both Telegram bots...")
    asyncio.run(main())