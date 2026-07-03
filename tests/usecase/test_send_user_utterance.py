import pytest

# 이 테스트가 쓰는 것들을 가져온다(import).
from voice_agent.domain.conversation import Conversation      # 대화(턴 모음) — 2교시
from voice_agent.domain.session_config import SessionConfig   # 세션 설정 값객체 — 2교시
from voice_agent.domain.turn import Role                      # 발화 주체(USER/ASSISTANT) — 2교시
from voice_agent.usecase.send_user_utterance import SendUserUtterance  # 아직 없음 → RED의 원인
from tests.usecase.fakes import FakeRealtimeSession


def test_utterance_is_recorded_and_reply_returned():
    # 준비(Arrange): 가짜 세션 + 빈 대화 + 유즈케이스를 조립한다.
    session = FakeRealtimeSession(reply="맑고 따뜻해요.")   # 항상 이 답을 주는 가짜
    convo = Conversation()                                 # 처음엔 턴이 하나도 없는 대화
    # 유즈케이스에 '가짜 세션'과 '대화'를 주입(DI). 진짜 대신 가짜가 들어간다.
    usecase = SendUserUtterance(session=session, conversation=convo)

    # 실행(Act): 사용자가 한마디 한다.
    reply = usecase.execute("오늘 날씨 어때?")

    # 검증(Assert) 1: 어시스턴트 응답이 그대로 반환된다.
    assert reply == "맑고 따뜻해요."

    # 검증 2: 대화에 '사용자 → 어시스턴트' 두 턴이 '순서대로' 쌓였다.
    assert len(convo.turns) == 2                    # 턴이 정확히 2개
    assert convo.turns[0].role == Role.USER         # 첫 턴은 사용자
    assert convo.turns[0].text == "오늘 날씨 어때?"
    assert convo.turns[1].role == Role.ASSISTANT    # 둘째 턴은 어시스턴트
    assert convo.turns[1].text == "맑고 따뜻해요."

    # 검증 3: 가짜 세션에 사용자 텍스트가 '실제로' 전달됐다(유즈케이스가 포트를 올바르게 호출).
    assert session.sent_texts == ["오늘 날씨 어때?"]


def test_empty_utterance_is_rejected():
    usecase = SendUserUtterance(
        session=FakeRealtimeSession(reply="응답"),
        conversation=Conversation(),
    )
    # 빈 문자열/공백만 있는 발화는 ValueError
    with pytest.raises(ValueError):
        usecase.execute("   ")