import asyncio, json, psutil, websockets, win32gui, win32process
from win10toast import ToastNotifier
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
WS_URL    = "ws://192.168.68.115:3000"
HEADERS   = {"X-Auth": "SUPERSECRET"}
USER_ID   = "vance"
DEVICE_ID = "pc-2"
POLL_SEC  = 5
RETRY_SEC = 5          # wait this long before reconnect attempts
# ──────────────────────────────────────────────────────────────────────────────

toast = ToastNotifier()   # reserved for future notifications


def get_foreground_exe() -> str:
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return "none"
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        return psutil.Process(pid).name()
    except psutil.Error:
        return "unknown.exe"


async def run_scout() -> None:
    while True:
        try:
            print(f"🔌  Connecting to {WS_URL} …")
            async with websockets.connect(WS_URL, extra_headers=HEADERS) as ws:
                print("✅ Connected — streaming events every", POLL_SEC, "s")
                while True:
                    event = {
                        "ts": datetime.now().isoformat(timespec="seconds"),
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
            print(f"⏳ Retrying in {RETRY_SEC} s …")
            await asyncio.sleep(RETRY_SEC)


if __name__ == "__main__":
    asyncio.run(run_scout())
