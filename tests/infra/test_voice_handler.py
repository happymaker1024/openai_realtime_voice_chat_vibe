from websockets.exceptions import ConnectionClosed

from voice_agent.adapter.async_realtime import AsyncRealtimeSession
from voice_agent.infra.voice_handler import RealtimeVoiceHandler


class ClosingFakeConnection:
    """자막 한 개를 준 뒤 ConnectionClosed를 던지는 가짜 연결 (= 중지 상황 재현)."""

    def __init__(self):
        self._events = [
            {"type": "response.output_audio_transcript.delta", "delta": "안녕"},
        ]

    async def send_event(self, event: dict) -> None:
        pass

    async def recv_event(self) -> dict:
        if self._events:
            return self._events.pop(0)   # 먼저 자막 한 개를 돌려주고
        raise ConnectionClosed(None, None)   # 그다음 정상 종료(1000 OK) 신호

    async def close(self) -> None:
        pass


async def test_read_events_stops_quietly_on_close():
    # 핸들러를 만들고, 내부 세션에 '닫히는 가짜 연결'을 꽂는다.
    handler = RealtimeVoiceHandler()
    handler._session = AsyncRealtimeSession(connection=ClosingFakeConnection())

    # 핵심: ConnectionClosed가 밖으로 새지 않고 '예외 없이' 끝나야 한다.
    # (try/except가 없으면 이 줄에서 예외가 터져 테스트가 실패한다.)
    await handler._read_events()