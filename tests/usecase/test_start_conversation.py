from voice_agent.domain.conversation import Conversation      # 대화(턴 모음)
from voice_agent.domain.session_config import SessionConfig   # 세션 설정 값객체
from voice_agent.usecase.start_conversation import StartConversation  # 아직 없음 → RED
from tests.usecase.fakes import FakeRealtimeSession


def test_start_opens_session_and_returns_empty_conversation():
    session = FakeRealtimeSession()                 # 준비: 가짜 세션
    usecase = StartConversation(session=session)    # 유즈케이스에 주입(DI)

    convo = usecase.execute(SessionConfig())        # 실행: 기본 설정으로 대화 시작

    # 검증 1: open()이 호출됐다(기록이 None이 아니다).
    assert session.opened_with is not None
    # 검증 2: 그때 넘어간 설정의 모델이 기본값이다.
    assert session.opened_with.model == "gpt-realtime"
    # 검증 3: 돌려받은 것이 Conversation 타입이고,
    assert isinstance(convo, Conversation)
    # 검증 4: 아직 발화가 없어 비어 있다.
    assert convo.turns == []