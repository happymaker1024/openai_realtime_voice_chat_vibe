import base64   # 테스트에서 base64를 되돌려(디코드) 원본 PCM과 비교하려고

from voice_agent.adapter.async_realtime import AsyncRealtimeSession  # 아직 없음 → RED
from voice_agent.domain.audio_frame import AudioFrame               # 오디오 한 조각
from voice_agent.domain.session_config import SessionConfig         # 세션 설정


class FakeAsyncConnection:
    """테스트용 가짜 async 연결. 보낸 이벤트를 기록한다.

    실제 소켓 없이, 메서드 모양(async send/recv/close)만 맞춰 세션에 끼운다.
    """

    def __init__(self):
        self.sent: list[dict] = []   # 세션이 보낸 이벤트를 순서대로 기록
        self.closed = False          # close() 호출 여부

    async def send_event(self, event: dict) -> None:
        self.sent.append(event)      # 보낸 것을 기록만(실제 전송 없음)

    async def recv_event(self) -> dict:
        return {}                    # 이 두 테스트에선 수신을 안 쓰므로 빈 dict

    async def close(self) -> None:
        self.closed = True


async def test_open_sends_audio_session_update():
    conn = FakeAsyncConnection()                       # 가짜 연결
    session = AsyncRealtimeSession(connection=conn)     # 세션에 주입

    await session.open(SessionConfig())                # 세션 열기(= session.update 전송)

    # 검증: 첫 전송이 session.update이고, 오디오 출력·올바른 모델로 열렸다.
    assert conn.sent[0]["type"] == "session.update"
    assert conn.sent[0]["session"]["output_modalities"] == ["audio"]
    assert conn.sent[0]["session"]["model"] == "gpt-realtime"


async def test_send_audio_appends_base64_pcm():
    conn = FakeAsyncConnection()
    session = AsyncRealtimeSession(connection=conn)

    # 4바이트짜리 가짜 PCM (int16 두 샘플). \x01\x00 = 1, \x02\x00 = 2 (리틀엔디언).
    frame = AudioFrame(sample_rate=24000, data=b"\x01\x00\x02\x00")
    await session.send_audio(frame)

    ev = conn.sent[0]                                        # 보낸 이벤트 하나를 꺼내
    assert ev["type"] == "input_audio_buffer.append"        # 오디오 추가 이벤트인지
    # base64를 '되돌리면(decode)' 원래 PCM 바이트가 그대로 나와야 한다 → 인코딩이 올바름.
    assert base64.b64decode(ev["audio"]) == b"\x01\x00\x02\x00"


async def test_close_closes_connection():
    conn = FakeAsyncConnection()
    session = AsyncRealtimeSession(connection=conn)

    await session.close()          # 세션을 닫으면

    assert conn.closed is True      # 내부 연결도 닫혀야 한다


async def test_cancel_sends_response_cancel():
    conn = FakeAsyncConnection()
    session = AsyncRealtimeSession(connection=conn)

    await session.cancel_response()

    assert conn.sent[-1]["type"] == "response.cancel"


async def test_open_includes_tools_when_given():
    conn = FakeAsyncConnection()
    session = AsyncRealtimeSession(connection=conn)

    tools = [{"type": "function", "name": "get_weather",
              "description": "날씨", "parameters": {"type": "object", "properties": {}, "required": []}}]
    await session.open(SessionConfig(), tools=tools)

    ev = conn.sent[0]
    # session.update 안에 tools와 tool_choice가 실려야 한다.
    assert ev["session"]["tools"] == tools
    assert ev["session"]["tool_choice"] == "auto"


async def test_send_tool_result_creates_function_output():
    conn = FakeAsyncConnection()
    session = AsyncRealtimeSession(connection=conn)

    await session.send_tool_result(call_id="call_abc", output='{"result": "맑음"}')

    ev = conn.sent[0]
    assert ev["type"] == "conversation.item.create"
    assert ev["item"]["type"] == "function_call_output"
    assert ev["item"]["call_id"] == "call_abc"          # 같은 call_id로 이어붙임
    assert ev["item"]["output"] == '{"result": "맑음"}'


async def test_request_response_sends_response_create():
    conn = FakeAsyncConnection()
    session = AsyncRealtimeSession(connection=conn)

    await session.request_response()

    assert conn.sent[0]["type"] == "response.create"