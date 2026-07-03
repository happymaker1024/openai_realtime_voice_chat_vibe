from voice_agent.adapter.transcript import extract_transcript_delta, extract_error_message


def test_returns_delta_for_transcript_event():
    event = {"type": "response.output_audio_transcript.delta", "delta": "안녕"}
    assert extract_transcript_delta(event) == "안녕"


def test_returns_none_for_other_events():
    assert extract_transcript_delta({"type": "response.output_audio.delta"}) is None
    assert extract_transcript_delta({"type": "session.updated"}) is None


def test_extracts_nested_error_message():
    # 실제 error 이벤트는 message가 error 객체 안에 중첩된다
    event = {"type": "error", "error": {"message": "rate limit"}}
    assert extract_error_message(event) == "rate limit"


def test_returns_none_when_no_error():
    assert extract_error_message({"type": "response.done"}) is None