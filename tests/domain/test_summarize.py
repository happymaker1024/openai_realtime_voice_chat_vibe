from voice_agent.domain.conversation import Conversation
from voice_agent.domain.summary import summarize
from voice_agent.domain.turn import Turn, Role


def test_summarize_counts_and_preview():
    # 사용자 발화 + 어시스턴트 발화로 턴 2개짜리 대화 구성
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="지금 몇 시야?"))
    convo.add_turn(Turn(role=Role.ASSISTANT, text="오후 3시예요."))

    out = summarize(convo)
    assert "2" in out                 # 턴 수
    assert "지금 몇 시" in out          # 첫 사용자 발화 미리보기


def test_summarize_empty():
    # 턴이 하나도 없는 빈 대화는 고정 문자열을 반환해야 한다
    assert summarize(Conversation()) == "빈 대화"
