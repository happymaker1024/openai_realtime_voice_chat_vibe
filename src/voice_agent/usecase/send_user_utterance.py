from voice_agent.domain.conversation import Conversation      # 대화(턴 모음)
from voice_agent.domain.turn import Turn, Role                 # 턴 한 개 + 발화 주체
from voice_agent.usecase.ports import RealtimeSessionPort      # 세션 '약속'(포트) — 진짜가 아니라 약속에만 의존


class SendUserUtterance:
    """사용자 한마디를 받아: 세션에 보내고, 응답을 대화에 기록하고, 돌려준다."""

    def __init__(self, session: RealtimeSessionPort, conversation: Conversation):
        # 생성자에서 '약속(포트)'과 '대화'를 주입받는다(의존성 주입, DI).
        # 타입 힌트가 RealtimeSessionPort라, 그 모양을 만족하면 진짜든 가짜든 받는다.
        self._session = session              # 통신을 맡길 세션(포트 구현체)
        self._conversation = conversation    # 오간 발화를 쌓아둘 대화
        # ↑ 앞의 밑줄(_)은 '이건 내부용'이라는 관례적 표시(파이썬에 강제성은 없음).

    def execute(self, user_text: str) -> str:
        """사용자 발화 한 번을 처리하고 어시스턴트 응답 텍스트를 반환한다."""

        # 공백을 제거했을 때 비어 있으면 처리하지 않는다
        if not user_text.strip():
            raise ValueError("빈 발화는 보낼 수 없습니다")

        # 1) 사용자 턴을 대화에 기록한다(방금 사용자가 한 말을 남긴다).
        self._conversation.add_turn(Turn(role=Role.USER, text=user_text))

        # 2) 세션(포트)에 보내고 응답을 받는다.
        #    이 한 줄이 진짜 OpenAI인지 가짜인지 유즈케이스는 '전혀 모른다' — 포트 뒤에 숨겨져 있다.
        reply_text = self._session.send_user_text(user_text)

        # 3) 어시스턴트 턴을 대화에 기록한다(받은 응답도 대화에 남긴다).
        self._conversation.add_turn(Turn(role=Role.ASSISTANT, text=reply_text))

        # 4) 응답 텍스트를 호출한 쪽에 돌려준다.
        return reply_text