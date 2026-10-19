import asyncio
import websockets

async def test():
    try:
        uri = "ws://127.0.0.1:8000/ws/chat/general/"
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ CONNECTED SUCCESSFULLY!")
            response = await websocket.recv()
            print(f"📩 Received: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test())