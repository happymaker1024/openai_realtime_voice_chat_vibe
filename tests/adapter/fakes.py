class FakeConnection:
    """어댑터 테스트들이 공유하는 가짜 연결."""

    def __init__(self, scripted_events: list[dict]):
        self.sent: list[dict] = []
        self._incoming = list(scripted_events)
        self.closed = False

    def send_event(self, event: dict) -> None:
        self.sent.append(event)

    def recv_event(self) -> dict:
        return self._incoming.pop(0)

    def close(self) -> None:
        self.closed = True