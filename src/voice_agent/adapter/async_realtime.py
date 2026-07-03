import base64                          # PCM 바이트 ↔ base64 문자열 변환용 표준 라이브러리
from typing import AsyncIterator       # async 제너레이터의 반환 타입 표기

from voice_agent.adapter.async_connection import AsyncRealtimeConnection  # 저수준 연결 '약속'
from voice_agent.domain.audio_frame import AudioFrame                     # 오디오 한 조각(2교시 값객체)
from voice_agent.domain.session_config import SessionConfig              # 세션 설정 값객체


class AsyncRealtimeSession:
    """오디오를 스트리밍하는 async Realtime 세션."""

    def __init__(self, connection: AsyncRealtimeConnection):
        # 저수준 연결(진짜 WebSocket이든 가짜든)을 주입받아 보관한다.
        self._conn = connection

    async def open(self, config: SessionConfig, tools: list[dict] | None = None) -> None:
        # 세션 설정(session.update)을 구성한다.
        session: dict = {
            "type": "realtime",
            "model": config.model,
            "output_modalities": ["audio"],
            "audio": {
                "input": {
                    "format": {"type": "audio/pcm", "rate": 24000},
                    "turn_detection": {"type": "semantic_vad"},
                    "transcription": {"model": "gpt-4o-mini-transcribe"},
                },
                "output": {
                    "format": {"type": "audio/pcm", "rate": 24000},
                    "voice": config.voice,
                },
            },
            "instructions": "You are a helpful voice assistant. 한국어로 짧고 자연스럽게 답하세요.",
        }
        # 도구가 주어졌을 때만 tools/tool_choice를 얹는다.
        if tools:
            session["tools"] = tools          # 모델이 쓸 수 있는 함수 목록
            session["tool_choice"] = "auto"   # 언제 쓸지는 모델이 알아서
        await self._conn.send_event({"type": "session.update", "session": session})

    async def send_tool_result(self, call_id: str, output: str) -> None:
        # 함수 실행 결과를 '대화 아이템'으로 모델에 돌려준다.
        await self._conn.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",   # 이 아이템이 '함수 결과'임을 표시
                "call_id": call_id,               # 아까 요청과 같은 영수증 번호
                "output": output,                 # 결과(JSON 문자열)
            },
        })

    async def request_response(self) -> None:
        # "이제 방금 받은 결과로 최종 응답을 만들어줘"라고 요청한다.
        await self._conn.send_event({"type": "response.create"})
        
    async def send_audio(self, frame: AudioFrame) -> None:
        # 오디오 한 조각을 Realtime에 흘려보낸다.
        # PCM 원본 바이트 → base64 문자열로 인코딩(JSON에 담아 보내려면 문자열이어야 함).
        b64 = base64.b64encode(frame.data).decode("ascii")
        await self._conn.send_event({
            "type": "input_audio_buffer.append",   # '입력 버퍼에 오디오 조각 추가' 이벤트
            "audio": b64,                          # base64로 인코딩한 오디오
        })
        # ※ commit/response.create를 우리가 안 보내도, 서버 VAD가 말끝을 감지해 알아서 응답한다.

    async def cancel_response(self) -> None:
        """진행 중인 응답 생성을 중단하도록 서버에 요청한다."""
        await self._conn.send_event({"type": "response.cancel"})

    async def events(self) -> AsyncIterator[dict]:
        # 서버 이벤트를 '끝없이' 하나씩 내보내는 async 제너레이터.
        # 호출한 쪽은 `async for event in session.events():` 로 받아 쓴다.
        while True:
            yield await self._conn.recv_event()   # 이벤트 하나를 받아(await) 내보낸다(yield)

    async def close(self) -> None:
        # 내부 연결을 닫는다.
        await self._conn.close()