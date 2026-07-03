from voice_agent.adapter.realtime_connection import RealtimeConnection  # 저수준 연결 '약속'
from voice_agent.domain.session_config import SessionConfig             # 세션 설정 값객체


class OpenAIRealtimeAdapter:
    """RealtimeSessionPort의 실제 구현. OpenAI Realtime 이벤트로 통신한다.

    (4교시는 텍스트 우선. 음성 입출력은 5·6교시에서 확장한다.)
    """

    def __init__(self, connection: RealtimeConnection):
        # 저수준 연결을 주입받는다(진짜 WebSocket이든 가짜든 상관없음).
        # 어댑터는 send_event/recv_event/close 세 가지만 쓰므로,
        # 그 모양만 맞으면 무엇이든 받아들인다.
        self._conn = connection

    def open(self, config: SessionConfig) -> None:
        # 세션을 시작하며 설정을 알려주는 첫 이벤트(session.update)를 보낸다.
        self._conn.send_event({
            "type": "session.update",            # 이벤트 종류: 세션 설정
            "session": {
                "type": "realtime",              # 실시간 세션임을 명시
                "model": config.model,           # 쓸 모델(SessionConfig 기본값 gpt-realtime)
                "output_modalities": ["text"],   # 4교시는 텍스트만 받는다(음성은 6교시)
                "instructions": "You are a helpful voice assistant.",  # 시스템 지시(성격/역할)
            },
        })

    def send_user_text(self, text: str) -> str:
        # 1) 사용자 입력 텍스트를 '대화 아이템'으로 추가한다.
        self._conn.send_event({
            "type": "conversation.item.create",  # 이벤트 종류: 대화에 아이템 추가
            "item": {
                "type": "message",               # 아이템 종류: 메시지
                "role": "user",                  # 이 메시지의 주체: 사용자
                "content": [{"type": "input_text", "text": text}],  # 입력 텍스트 본문
            },
        })

        # 2) "이제 응답을 만들어 달라"고 요청한다(텍스트 형태로).
        self._conn.send_event({
            "type": "response.create",                        # 이벤트 종류: 응답 생성 요청
            "response": {"output_modalities": ["text"]},      # 응답도 텍스트로 받겠다
        })

        # 3) 서버가 보내오는 이벤트들을 '끝날 때까지' 읽으며 텍스트 조각을 모은다.
        chunks: list[str] = []          # 조각(delta)들을 담을 리스트
        while True:                     # 끝(response.done)을 만날 때까지 반복
            event = self._conn.recv_event()      # 서버 이벤트 하나를 받는다
            etype = event.get("type")            # 그 이벤트의 종류를 꺼낸다

            if etype == "response.output_text.delta":
                # 텍스트 조각이면 모은다. 'delta' 키가 없으면 빈 문자열로.
                chunks.append(event.get("delta", ""))
            elif etype == "response.done":
                break                            # 끝 신호 → 반복 종료
            elif etype == "error":
                # 실제 error 이벤트는 message가 error 객체 '안에' 중첩돼 있다:
                #   {"type": "error", "error": {"message": "...", ...}}
                # event.get("error", event): error 객체가 있으면 그걸, 없으면 event 자체를 쓴다.
                err = event.get("error", event)
                # 실제 메시지를 담아 예외를 던진다(메시지가 없으면 이벤트 전체를 문자열로).
                raise RuntimeError(err.get("message") or str(event))
            # 그 밖의 이벤트(session.created 등)는 어느 분기에도 안 걸리므로 그냥 무시하고 계속 읽는다.

        # 모은 조각들을 순서대로 이어붙여 완성된 한 문장으로 만든다.
        return "".join(chunks)

    def close(self) -> None:
        # 연결을 닫는다(정리).
        self._conn.close()