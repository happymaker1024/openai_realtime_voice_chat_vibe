import json
import os

from websocket import create_connection  # websocket-client 라이브러리


class WebSocketConnection:
    """실제 OpenAI Realtime WebSocket 연결. RealtimeConnection 약속을 만족한다."""

    def __init__(self, model: str = "gpt-realtime"):
        api_key = os.environ["OPENAI_API_KEY"]   # .env에서 load_dotenv로 올라온 키
        # GA 인터페이스: 베타 헤더 없이 Authorization 헤더로 연결
        self._ws = create_connection(
            f"wss://api.openai.com/v1/realtime?model={model}",
            header=[f"Authorization: Bearer {api_key}"],
        )

    def send_event(self, event: dict) -> None:
        self._ws.send(json.dumps(event))

    def recv_event(self) -> dict:
        return json.loads(self._ws.recv())

    def close(self) -> None:
        self._ws.close()