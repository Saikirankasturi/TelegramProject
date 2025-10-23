# run_both_loop.py
from multiprocessing import Process
import subprocess
import time

def run_forwarder():
    subprocess.run(["python", "forwarder.py"])

def run_bot():
    subprocess.run(["python", "bot.py"])

if __name__ == "__main__":
    while True:
        print("🔄 Starting bot and forwarder...")
        p1 = Process(target=run_forwarder)
        p2 = Process(target=run_bot)

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        print("🕐 Waiting 60 seconds before restart...")
        time.sleep(60)