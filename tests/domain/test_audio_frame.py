import pytest  # 예외(에러) 발생을 테스트하는 도구

from voice_agent.domain.audio_frame import AudioFrame


def test_valid_frame():
    # 올바른 값이면 그대로 만들어져야 한다
    frame = AudioFrame(sample_rate=24000, data=b"\x00\x01")

    assert frame.sample_rate == 24000
    assert frame.data == b"\x00\x01"


def test_zero_sample_rate_is_rejected():
    # 샘플레이트가 0이면 만들 때 ValueError가 나야 한다
    # pytest.raises(...) 블록 안에서 '그 에러가 발생하는지'를 검사
    with pytest.raises(ValueError):
        AudioFrame(sample_rate=0, data=b"\x00")


def test_empty_data_is_rejected():
    # 데이터가 비어 있으면 ValueError가 나야 한다
    with pytest.raises(ValueError):
        AudioFrame(sample_rate=24000, data=b"")