import os
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

router = APIRouter(tags=["Tiempo real"])

REDIS_URL = os.getenv("REDIS_URL")


@router.websocket("/ws/boards/{board_id}")
async def board_websocket(websocket: WebSocket, board_id: int):
    """
    Conexion en tiempo real para un tablero concreto. Cuando alguien
    se conecta aqui, se suscribe al canal de Redis de ese tablero, y
    reenvia cualquier mensaje que llegue a ese canal hacia el frontend.
    """
    await websocket.accept()

    redis_client = redis.from_url(REDIS_URL)
    pubsub = redis_client.pubsub()
    channel_name = f"board:{board_id}"
    await pubsub.subscribe(channel_name)

    try:
        # Bucle infinito: espera mensajes de Redis y los reenvia al
        # navegador, hasta que la conexion se cierre
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is not None:
                await websocket.send_text(message["data"].decode())
            # Un pequeño respiro para no consumir CPU sin necesidad
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        # El usuario cerro la pestaña o perdio la conexion
        pass
    finally:
        await pubsub.unsubscribe(channel_name)
        await redis_client.aclose()


async def publish_board_update(board_id: int, event_type: str, data: dict):
    """
    Funcion auxiliar que usaremos desde las rutas de listas y tarjetas:
    publica un evento en el canal de Redis de un tablero, para que
    todos los conectados por WebSocket a ese tablero se enteren.
    """
    redis_client = redis.from_url(REDIS_URL)
    channel_name = f"board:{board_id}"
    message = json.dumps({"event": event_type, "data": data})
    await redis_client.publish(channel_name, message)
    await redis_client.aclose()