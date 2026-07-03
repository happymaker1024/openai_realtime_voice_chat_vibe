from voice_agent.domain.session_config import SessionConfig


def test_defaults():
    # 아무 인자 없이 만들면 '약속된 기본값'이 들어가야 한다
    cfg = SessionConfig()

    assert cfg.model == "gpt-realtime"    # 접근성 넓은 GA 실시간 모델
    assert cfg.voice == "alloy"           # 기본 음성
    assert cfg.reasoning_effort == "low"  # 1교시에서 정한 비용·지연 절약 기본값


def test_override():
    # 일부만 바꿔도, 나머지는 기본값을 유지해야 한다
    cfg = SessionConfig(voice="verse", reasoning_effort="medium")

    assert cfg.voice == "verse"            # 바꾼 값은 반영
    assert cfg.reasoning_effort == "medium"
    assert cfg.model == "gpt-realtime"     # 안 바꾼 값은 그대로 기본값