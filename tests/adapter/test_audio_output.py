import base64          # PCM ↔ base64 변환
import numpy as np      # 오디오 숫자 배열을 다루는 라이브러리

from voice_agent.adapter.audio_output import decode_audio_delta   # 아직 없음 → RED
from voice_agent.adapter.audio_output import is_speech_started


def test_decodes_pcm16_audio_delta():
    # 준비: int16 샘플 3개[1, -2, 3]를 리틀엔디언 PCM 바이트로 만들고, base64로 감싸 이벤트에 싣는다.
    pcm = np.array([1, -2, 3], dtype="<i2").tobytes()
    event = {"type": "response.output_audio.delta",
             "delta": base64.b64encode(pcm).decode("ascii")}

    out = decode_audio_delta(event)   # 실행: 디코드

    assert out is not None            # 음성 이벤트이므로 None이 아니어야
    assert out.dtype == np.int16      # int16으로 해석됐는지
    assert out.tolist() == [1, -2, 3]  # 원래 샘플이 그대로 복원됐는지


def test_returns_none_for_non_audio_event():
    # 음성이 아닌 이벤트(자막/완료)에는 None을 돌려줘야 한다.
    assert decode_audio_delta({"type": "response.output_audio_transcript.delta"}) is None
    assert decode_audio_delta({"type": "response.done"}) is None


def test_true_on_speech_started():
    assert is_speech_started({"type": "input_audio_buffer.speech_started"}) is True


def test_false_on_other_events():
    assert is_speech_started({"type": "response.output_audio.delta"}) is False
    assert is_speech_started({"type": "response.done"}) is False


def test_returns_none_when_audio_missing():
    # 음성 이벤트지만 base64가 비었거나 없음
    assert decode_audio_delta({"type": "response.output_audio.delta", "delta": ""}) is None
    assert decode_audio_delta({"type": "response.output_audio.delta"}) is None