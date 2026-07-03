import base64          # base64 문자열 → 바이트 디코드
import numpy as np      # 바이트 → 숫자 배열 해석


def decode_audio_delta(event: dict) -> np.ndarray | None:
    """음성 델타 이벤트면 base64 PCM16을 int16 배열로 디코드해 돌려준다.
    음성 이벤트가 아니면 None.
    """
    # 1) 음성 델타 이벤트가 아니면 즉시 None(관심 밖).
    if event.get("type") != "response.output_audio.delta":
        return None
    # 2) 서버 버전에 따라 base64가 'delta' 또는 'audio' 필드에 올 수 있어 둘 다 대응.
    #    ('delta'가 있으면 그걸, 없으면 'audio'를 쓴다.)
    b64 = event.get("delta") or event.get("audio")
    # 3) 알맹이가 비어 있으면(빈 문자열/None) 안전하게 None.
    if not b64:
        return None
    # 4) base64 문자열을 원본 PCM 바이트로 되돌린다.
    pcm = base64.b64decode(b64)
    # 5) 그 바이트를 리틀엔디언 int16 배열로 '해석'한다.
    #    frombuffer는 원본을 가리키는 읽기전용 '뷰'라, .copy()로 쓰기 가능한 복사본을 만든다.
    return np.frombuffer(pcm, dtype="<i2").copy()


def is_speech_started(event: dict) -> bool:
    """사용자가 말을 시작했다는 신호면 True (바지인 트리거)."""
    return event.get("type") == "input_audio_buffer.speech_started"