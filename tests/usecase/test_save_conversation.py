from voice_agent.domain.conversation import Conversation
from voice_agent.domain.turn import Turn, Role
from voice_agent.usecase.save_conversation import SaveConversation


class FakeStore:
    """테스트용 가짜 저장소. 무엇을 저장했는지 기록한다."""
    def __init__(self):
        self.saved = None

    def save(self, session_id, conversation):
        self.saved = (session_id, conversation)


def test_saves_and_returns_summary():
    store = FakeStore()
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="안녕"))

    usecase = SaveConversation(store=store)
    summary = usecase.execute(convo, session_id="sess-9")

    # 저장이 실제로 호출됐고(같은 대화·id)
    assert store.saved[0] == "sess-9"
    assert store.saved[1] is convo
    # 반환값이 요약이다
    assert "1" in summary


class FakeSummarizer:
    """정상 동작하는 가짜 요약기. 고정 문장을 돌려준다."""

    def summarize(self, conversation):
        return "사용자가 인사를 건넸다."


class BrokenSummarizer:
    """항상 실패하는 가짜 요약기(네트워크 오류 등을 흉내)."""

    def summarize(self, conversation):
        raise RuntimeError("모델 호출 실패")


def test_uses_summarizer_when_provided():
    store = FakeStore()
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="안녕"))

    usecase = SaveConversation(store=store, summarizer=FakeSummarizer())
    summary = usecase.execute(convo, session_id="sess-9")

    assert summary == "사용자가 인사를 건넸다."


def test_falls_back_to_domain_summary_when_summarizer_fails():
    store = FakeStore()
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="안녕"))

    usecase = SaveConversation(store=store, summarizer=BrokenSummarizer())
    summary = usecase.execute(convo, session_id="sess-9")

    # 모델 요약이 실패하면 도메인 summarize() 결과로 폴백해야 한다
    assert "1" in summary
    assert "안녕" in summary
