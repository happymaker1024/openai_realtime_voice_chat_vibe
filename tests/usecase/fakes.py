from voice_agent.domain.session_config import SessionConfig


class FakeRealtimeSession:
    """유즈케이스 테스트들이 공유하는 가짜 세션."""

    def __init__(self, reply: str = ""):
        self.reply = reply
        self.opened_with: SessionConfig | None = None
        self.sent_texts: list[str] = []

    def open(self, config: SessionConfig) -> None:
        self.opened_with = config

    def send_user_text(self, text: str) -> str:
        self.sent_texts.append(text)
        return self.reply

    def close(self) -> None:
        self.opened_with = None