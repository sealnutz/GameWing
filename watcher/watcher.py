import asyncio
import json
import psutil
import websockets
import win32gui
import win32process
from win10toast import ToastNotifier
from datetime import datetime  # New import for ISO timestamp

WS_URL = "ws://localhost:3000"  # Hub server URL
POLL_SEC = 5                    # Seconds between samples
toast = ToastNotifier()         # Reserved for future notifications

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

async def main() -> None:
    headers = {
        "X-Auth": "changeme"  # Must match SHARED_TOKEN from .env
    }
    async with websockets.connect(WS_URL, extra_headers=headers) as ws:
        while True:
            event = {
                "ts": datetime.now().isoformat(timespec="seconds"),  # fixed timestamp format
                "app": get_foreground_exe(),
                "state": "ACTIVE_FOREGROUND",
                "user_id": "sealn",     # Update per PC
                "device_id": "PC1"      # Update per PC
            }
            await ws.send(json.dumps(event))
            print(event)
            await asyncio.sleep(POLL_SEC)

if __name__ == "__main__":
    asyncio.run(main())
