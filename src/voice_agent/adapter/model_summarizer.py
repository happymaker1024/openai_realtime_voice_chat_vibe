from typing import Protocol

from voice_agent.adapter.openai_realtime import OpenAIRealtimeAdapter
from voice_agent.adapter.websocket_connection import WebSocketConnection
from voice_agent.domain.conversation import Conversation
from voice_agent.domain.session_config import SessionConfig


class _TextSession(Protocol):
    """요약에 필요한 만큼만 좁힌 세션 모양(open/send_user_text/close)."""

    def open(self, config: SessionConfig) -> None: ...
    def send_user_text(self, text: str) -> str: ...
    def close(self) -> None: ...


def _build_prompt(conversation: Conversation) -> str:
    # 대화를 "역할: 텍스트" 줄로 정리해 모델에게 통째로 건넨다.
    lines = [f"{turn.role.value}: {turn.text}" for turn in conversation.turns]
    transcript = "\n".join(lines)
    return (
        "다음은 사용자와 음성 비서의 대화 기록이다. "
        "사람이 읽기 좋은 한 문장으로 자연스럽게 요약해줘.\n\n"
        f"{transcript}"
    )


class ModelSummarizer:
    """대화를 모델에게 보내 한 문장 요약을 받는 어댑터. SummarizerPort 약속을 만족한다.

    session을 주입하지 않으면 기존 텍스트 세션 방식(OpenAIRealtimeAdapter + WebSocketConnection)으로
    직접 연결한다. 실패하면(네트워크 등) 예외를 그대로 던진다 — 폴백 여부는 유즈케이스가 정한다.
    """

    def __init__(self, session: _TextSession | None = None, model: str = "gpt-realtime"):
        self._session = session
        self._model = model

    def summarize(self, conversation: Conversation) -> str:
        session = self._session or OpenAIRealtimeAdapter(connection=WebSocketConnection(model=self._model))
        session.open(SessionConfig(model=self._model))
        try:
            reply = session.send_user_text(_build_prompt(conversation))
        finally:
            session.close()
        return reply.strip()
