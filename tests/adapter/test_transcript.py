from voice_agent.adapter.transcript import (
    extract_error_message,
    extract_transcript_delta,
    extract_user_transcript,
)


def test_returns_delta_for_transcript_event():
    event = {"type": "response.output_audio_transcript.delta", "delta": "안녕"}
    assert extract_transcript_delta(event) == "안녕"


def test_returns_none_for_other_events():
    assert extract_transcript_delta({"type": "response.output_audio.delta"}) is None
    assert extract_transcript_delta({"type": "session.updated"}) is None


def test_returns_transcript_for_user_transcription_completed_event():
    event = {
        "type": "conversation.item.input_audio_transcription.completed",
        "transcript": "오늘 날씨 알려줘",
    }
    assert extract_user_transcript(event) == "오늘 날씨 알려줘"


def test_returns_none_for_non_user_transcription_events():
    assert extract_user_transcript({"type": "response.output_audio_transcript.delta"}) is None
    assert extract_user_transcript({"type": "session.updated"}) is None


def test_extracts_nested_error_message():
    # 실제 error 이벤트는 message가 error 객체 안에 중첩된다
    event = {"type": "error", "error": {"message": "rate limit"}}
    assert extract_error_message(event) == "rate limit"


def test_returns_none_when_no_error():
    assert extract_error_message({"type": "response.done"}) is None