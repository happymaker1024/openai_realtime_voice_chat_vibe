from voice_agent.adapter.openai_realtime import OpenAIRealtimeAdapter  # 진짜 어댑터
from voice_agent.domain.conversation import Conversation              # 대화(턴 모음)
from voice_agent.domain.turn import Role                              # 발화 주체
from voice_agent.usecase.send_user_utterance import SendUserUtterance  # 3교시 유즈케이스
from tests.adapter.fakes import FakeConnection


def test_usecase_uses_real_adapter():
    # 준비: 서버가 '인사말 한 조각 → 완료' 순으로 보낸다는 대본.
    conn = FakeConnection([
        {"type": "response.output_text.delta", "delta": "안녕하세요!"},
        {"type": "response.done", "response": {}},
    ])
    # 유즈케이스에 '진짜 어댑터'를 주입한다(단, 그 안의 연결만 가짜).
    # → 3교시에선 세션 자체가 가짜였지만, 여기선 진짜 어댑터 + 가짜 연결이다.
    adapter = OpenAIRealtimeAdapter(connection=conn)
    convo = Conversation()
    usecase = SendUserUtterance(session=adapter, conversation=convo)

    # 실행: 유즈케이스를 통해 한마디 보낸다.
    reply = usecase.execute("안녕")

    # 검증 1: 응답이 어댑터를 거쳐 그대로 흘러나온다.
    assert reply == "안녕하세요!"
    # 검증 2: 대화에 사용자 → 어시스턴트 턴이 순서대로 쌓였다.
    assert convo.turns[0].role == Role.USER
    assert convo.turns[1].role == Role.ASSISTANT
    assert convo.turns[1].text == "안녕하세요!"