from typing import Protocol   # '이런 메서드가 있어야 한다'는 약속(인터페이스)을 만드는 도구


class RealtimeConnection(Protocol):
    """어댑터와 실제 통신 채널 사이의 얇은 약속(저수준 시드).

    어댑터는 이 약속에만 의존한다.
    진짜 구현(WebSocket)은 선택 과제, 가짜(Fake)는 테스트에서 쓴다.
    """

    def send_event(self, event: dict) -> None:
        """클라이언트 이벤트(JSON dict)를 서버로 보낸다."""
        ...   # 실제 전송 방법(소켓 write 등)은 구현이 채운다

    def recv_event(self) -> dict:
        """서버가 보낸 이벤트(JSON dict) 하나를 받는다."""
        ...   # 실제 수신 방법(소켓 read 등)은 구현이 채운다

    def close(self) -> None:
        """연결을 닫는다."""
        ...