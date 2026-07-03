from voice_agent.domain.conversation import Conversation      # 돌려줄 빈 대화
from voice_agent.domain.session_config import SessionConfig   # 세션을 열 때 쓰는 설정
from voice_agent.usecase.ports import RealtimeSessionPort     # 세션 '약속'(포트)


class StartConversation:
    """세션을 열고, 비어 있는 새 대화를 만들어 돌려준다."""

    def __init__(self, session: RealtimeSessionPort):
        # 세션(포트 구현체)을 주입받아 보관한다(DI).
        self._session = session

    def execute(self, config: SessionConfig) -> Conversation:
        # 1) 주어진 설정으로 세션을 연다(내부적으로 session.update가 나간다 — 4교시 어댑터).
        self._session.open(config)
        # 2) 아직 발화가 없는 '빈 대화'를 만들어 돌려준다.
        #    이후 실제 발화는 SendUserUtterance가 이 대화에 채워 넣는다.
        return Conversation()