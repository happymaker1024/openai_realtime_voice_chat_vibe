import json
import os

import websockets


class AsyncWebSocketConnection:
    """실제 OpenAI Realtime async WebSocket 연결. AsyncRealtimeConnection 약속을 만족한다."""

    def __init__(self, ws):
        self._ws = ws

    @classmethod
    async def connect(cls, model: str) -> "AsyncWebSocketConnection":
        api_key = os.environ["OPENAI_API_KEY"]   # .env에서 load_dotenv로 올라온 키
        ws = await websockets.connect(
            f"wss://api.openai.com/v1/realtime?model={model}",
            additional_headers={"Authorization": f"Bearer {api_key}"},
        )
        return cls(ws)

    async def send_event(self, event: dict) -> None:
        await self._ws.send(json.dumps(event))

    async def recv_event(self) -> dict:
        return json.loads(await self._ws.recv())

    async def close(self) -> None:
        await self._ws.close()