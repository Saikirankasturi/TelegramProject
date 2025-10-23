# run_both.py
import asyncio
from bot import main as run_bot
from forwarder import main as run_forwarder

async def main():
    # Run both bots concurrently
    await asyncio.gather(
        run_bot(),
        run_forwarder()
    )

if __name__ == "__main__":
    asyncio.run(main())
