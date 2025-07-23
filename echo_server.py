import asyncio, websockets

async def echo(ws):
    async for msg in ws:
        print("From scout:", msg)
        await ws.send(msg)

async def main():
    # removed path=...
    async with websockets.serve(echo, "localhost", 8765):
        print("Echo running on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
