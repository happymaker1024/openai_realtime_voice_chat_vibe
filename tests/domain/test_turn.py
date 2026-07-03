from voice_agent.domain.turn import Turn, Role
from voice_agent.domain.audio_frame import AudioFrame


def test_turn_holds_role_and_text():
    # Turn 객체를 USER 역할과 텍스트로 생성
    turn = Turn(role=Role.USER, text="오늘 날씨 어때?")

    # Turn 객체의 role이 USER인지 확인
    assert turn.role == Role.USER
    # Turn 객체의 text가 올바르게 저장되었는지 확인
    assert turn.text == "오늘 날씨 어때?"


def test_turn_can_carry_optional_audio():
    # 음성 데이터를 함께 담은 턴을 만들 수 있어야 한다
    frame = AudioFrame(sample_rate=24000, data=b"\x00\x01")
    turn = Turn(role=Role.USER, text="안녕", audio=frame)

    assert turn.audio is frame  # 넣어준 그 프레임이 그대로 들어 있는가


def test_turn_audio_defaults_to_none():
    # audio를 안 주면 기본은 None(없음)이어야 한다
    turn = Turn(role=Role.ASSISTANT, text="네")
    assert turn.audio is None