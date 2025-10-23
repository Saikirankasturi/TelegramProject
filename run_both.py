import asyncio
import os
import json
from forwarder import start_forwarder
from bot import start_bot

# --- Make sure environment variables are set ---
required_env = ["BOT_TOKEN", "GOOGLE_CREDS", "SHEET_ID", "TARGET_CHAT_ID"]
for var in required_env:
    if not os.environ.get(var):
        raise ValueError(f"{var} environment variable is missing!")

# --- Run both bots concurrently ---
async def main():
    # start_forwarder() and start_bot() should be async functions
    await asyncio.gather(
        start_forwarder(),
        start_bot()
    )

if __name__ == "__main__":
    print("🚀 Running both Telegram bots...")
    asyncio.run(main())