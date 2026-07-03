import pytest

from voice_agent.adapter.openai_realtime import OpenAIRealtimeAdapter  # 아직 없음 → RED의 원인
from voice_agent.domain.session_config import SessionConfig            # 세션 설정 값객체 — 2교시
from tests.adapter.fakes import FakeConnection


def test_text_round_trip():
    # 준비: 서버가 '텍스트 조각 두 개 → 완료(done)' 순서로 보낸다고 가정한 대본.
    conn = FakeConnection(scripted_events=[
        {"type": "response.output_text.delta", "delta": "맑고 "},      # 조각 1
        {"type": "response.output_text.delta", "delta": "따뜻해요."},  # 조각 2
        {"type": "response.done", "response": {}},                     # 끝 신호
    ])
    adapter = OpenAIRealtimeAdapter(connection=conn)   # 어댑터에 가짜 연결 주입

    # 실행: 세션을 열고, 사용자 텍스트 한 턴을 보낸다.
    adapter.open(SessionConfig())
    reply = adapter.send_user_text("오늘 날씨 어때?")

    # 검증 1: 흩어진 조각(delta)들이 이어붙어 완성 문장이 된다.
    assert reply == "맑고 따뜻해요."

    # 검증 2: 어댑터가 '맨 처음' 보낸 건 session.update이고, 모델이 올바르다.
    #         (conn.sent[0] = 첫 번째로 보낸 이벤트)
    assert conn.sent[0]["type"] == "session.update"
    assert conn.sent[0]["session"]["model"] == "gpt-realtime"

    # 검증 3: 두 번째로 사용자 입력을 input_text 형태로 전달했다.
    #         중첩 dict를 단계별로 파고들어 실제 텍스트까지 확인한다.
    assert conn.sent[1]["type"] == "conversation.item.create"
    assert conn.sent[1]["item"]["content"][0]["text"] == "오늘 날씨 어때?"

    # 검증 4: 세 번째로 '응답을 만들어달라'(response.create)고 요청했다.
    assert conn.sent[2]["type"] == "response.create"


def test_error_event_raises():
    # 실제 서버 error 이벤트의 모양: message가 error 객체 안에 중첩된다
    conn = FakeConnection(scripted_events=[
        {"type": "error", "error": {"message": "rate limit"}},
    ])
    adapter = OpenAIRealtimeAdapter(connection=conn)
    adapter.open(SessionConfig())

    # send_user_text 도중 error 를 만나면 RuntimeError 가 나야 한다.
    # match= 로 '실제 메시지'가 예외에 실려 오는지까지 확인한다.
    with pytest.raises(RuntimeError, match="rate limit"):
        adapter.send_user_text("안녕")