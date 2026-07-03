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


class UserTranscriptFakeConnection:
    """사용자 입력 전사 완료 이벤트 한 개를 준 뒤 종료하는 가짜 연결."""

    def __init__(self):
        self._events = [
            {
                "type": "conversation.item.input_audio_transcription.completed",
                "transcript": "오늘 날씨 알려줘",
            },
        ]

    async def send_event(self, event: dict) -> None:
        pass

    async def recv_event(self) -> dict:
        if self._events:
            return self._events.pop(0)
        raise ConnectionClosed(None, None)

    async def close(self) -> None:
        pass


async def test_user_transcription_completed_adds_user_turn():
    from voice_agent.domain.turn import Role

    handler = RealtimeVoiceHandler()
    handler._session = AsyncRealtimeSession(connection=UserTranscriptFakeConnection())

    await handler._read_events()

    assert len(handler._conversation.turns) == 1
    turn = handler._conversation.turns[0]
    assert turn.role == Role.USER
    assert turn.text == "오늘 날씨 알려줘"