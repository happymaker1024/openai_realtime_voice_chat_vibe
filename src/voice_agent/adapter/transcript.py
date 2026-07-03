def extract_transcript_delta(event: dict) -> str | None:
    """자막(transcript) 조각 이벤트면 그 텍스트를, 아니면 None을 돌려준다."""
    if event.get("type") == "response.output_audio_transcript.delta":
        return event.get("delta", "")
    return None


def extract_user_transcript(event: dict) -> str | None:
    """사용자 입력 전사 완료 이벤트면 그 텍스트를, 아니면 None을 돌려준다."""
    if event.get("type") == "conversation.item.input_audio_transcription.completed":
        return event.get("transcript", "")
    return None


def extract_error_message(event: dict) -> str | None:
    """error 이벤트면 (중첩된) 메시지를, 아니면 None을 돌려준다."""
    if event.get("type") == "error":
        err = event.get("error", event)   # 실제 message는 error 객체 안에 중첩
        return err.get("message") or "unknown error"
    return None