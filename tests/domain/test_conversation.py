from voice_agent.domain.conversation import Conversation
from voice_agent.domain.turn import Turn, Role


def test_new_conversation_is_empty():
    # 새로운 대화는 빈 상태로 초기화되어야 함
    convo = Conversation()
    assert convo.turns == []


def test_add_turn_appends():
    # add_turn 메서드가 턴을 리스트에 추가하는지 확인
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="안녕"))

    assert len(convo.turns) == 1
    assert convo.turns[0].text == "안녕"


def test_last_user_text_returns_most_recent_user_utterance():
    # last_user_text 메서드가 가장 최근의 사용자 발화를 반환하는지 확인
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="첫 질문"))
    convo.add_turn(Turn(role=Role.ASSISTANT, text="답변"))
    convo.add_turn(Turn(role=Role.USER, text="두 번째 질문"))

    assert convo.last_user_text() == "두 번째 질문"


def test_assistant_replies_returns_only_assistant_texts():
    # 사용자/어시스턴트가 섞인 대화에서, 어시스턴트 발화만 모이는지 확인
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="안녕"))
    convo.add_turn(Turn(role=Role.ASSISTANT, text="네 안녕하세요"))
    convo.add_turn(Turn(role=Role.USER, text="날씨는?"))
    convo.add_turn(Turn(role=Role.ASSISTANT, text="맑아요"))

    # 어시스턴트 발화 텍스트만, 말한 순서대로
    assert convo.assistant_replies() == ["네 안녕하세요", "맑아요"]