from typing import Protocol   # '이런 메서드를 가진 무언가'라는 약속(인터페이스)을 만드는 도구

from voice_agent.domain.session_config import SessionConfig  # 2교시에서 만든 세션 설정 값객체
from voice_agent.domain.tool_spec import ToolSpec


class RealtimeSessionPort(Protocol):
    """음성/텍스트 세션과 통신하기 위한 '약속(인터페이스)'.

    유즈케이스는 이 약속에만 의존한다.
    진짜 구현(OpenAI)은 4교시, 가짜 구현(Fake)은 이번 교시에서 만든다.
    """

    def open(self, config: SessionConfig) -> None:
        """주어진 설정으로 세션을 연다."""
        ...   # 본문 없음 — '이런 메서드가 있어야 한다'는 모양만 선언한다

    def send_user_text(self, text: str) -> str:
        """사용자 텍스트를 보내고, 어시스턴트 응답 텍스트를 받는다."""
        ...   # 실제 통신 코드는 어댑터(진짜/가짜)가 채운다

    def close(self) -> None:
        """세션을 닫는다."""
        ...


class ToolRegistryPort(Protocol):
    """등록된 도구 명세 전체를 돌려주는 약속."""

    def all_specs(self) -> list[ToolSpec]:
        """등록된 모든 도구의 명세를 돌려준다."""
        ...