"""
Scout – GameWing desktop agent
Streams active‑window information to Beacon via WebSocket.
"""

import os, time, asyncio, json
import psutil, websockets, win32gui, win32process
from win10toast import ToastNotifier
from dotenv import load_dotenv, find_dotenv

# ─── Load per‑machine settings (.env in the same folder) ─────────────────────
load_dotenv(find_dotenv())                    # auto‑detects scout/.env

WS_URL    = os.getenv("WS_URL")               # wss://arius-beacon.ngrok.app
HEADERS   = {"X-Auth": os.getenv("X_AUTH", "")}
USER_ID   = os.getenv("USER_ID", "unknown")
DEVICE_ID = os.getenv("DEVICE_ID", "unknown-device")

POLL_SEC  = int(os.getenv("POLL_SEC", 5))
RETRY_SEC = int(os.getenv("RETRY_SEC", 5))
# ─────────────────────────────────────────────────────────────────────────────

toast = ToastNotifier()   # reserved for future notifications


def get_foreground_exe() -> str:
    """Return the executable name of the current foreground window."""
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return "none"
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        return psutil.Process(pid).name()
    except psutil.Error:
        return "unknown.exe"


async def run_scout() -> None:
    """Main loop: connect → send event every POLL_SEC → reconnect on failure."""
    while True:
        try:
            print(f"🔌  Connecting to {WS_URL} …")
            async with websockets.connect(WS_URL, extra_headers=HEADERS) as ws:
                print("✅  Connected — streaming events every", POLL_SEC, "s")
                while True:
                    event = {
                        "ts": int(time.time() * 1000),  # epoch‑ms BIGINT
                        "app": get_foreground_exe(),
                        "state": "ACTIVE_FOREGROUND",
                        "user_id": USER_ID,
                        "device_id": DEVICE_ID
                    }
                    await ws.send(json.dumps(event))
                    print(event)
                    await asyncio.sleep(POLL_SEC)
        except Exception as e:
            print("⚠️  Connection problem:", e)
            print(f"⏳  Retrying in {RETRY_SEC} s …")
            await asyncio.sleep(RETRY_SEC)


if __name__ == "__main__":
    asyncio.run(run_scout())
