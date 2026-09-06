# Script temporal solo para probar el WebSocket manualmente
# (no forma parte de la aplicacion en si)
import asyncio
import websockets


async def escuchar():
    uri = "ws://127.0.0.1:8000/ws/boards/1"
    async with websockets.connect(uri) as websocket:
        print("Conectado. Esperando eventos del tablero 1...")
        async for message in websocket:
            print("Evento recibido:", message)


asyncio.run(escuchar())