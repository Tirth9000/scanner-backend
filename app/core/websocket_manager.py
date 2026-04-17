from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    def connect(self, user_id: str, websocket: WebSocket):
        self.connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)

    async def send(self, user_id: str, payload: dict):
        ws = self.connections.get(user_id)
        if ws:
            await ws.send_json(payload)


ws_manager = WebSocketManager()
