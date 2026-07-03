from dataclasses import dataclass


@dataclass(frozen=True)
class AudioFrame:
    """오디오 한 조각: 샘플레이트 + 실제 음성 바이트.

    도메인은 numpy 같은 외부 라이브러리에 의존하지 않으므로,
    데이터는 파이썬 표준 타입인 bytes로 받는다.
    (numpy 배열 <-> bytes 변환은 바깥 계층인 어댑터의 몫 — 5교시)
    """

    sample_rate: int  # 1초당 샘플 수. 예: 24000 = 24kHz
    data: bytes       # PCM 오디오 원본 바이트

    def __post_init__(self) -> None:
        # __post_init__: dataclass가 필드를 다 채운 '직후' 자동으로 한 번 호출되는 검증 훅.
        # 여기서 규칙을 어기면 객체 생성 자체를 막는다(에러를 던진다).
        if self.sample_rate <= 0:
            raise ValueError("sample_rate는 0보다 커야 합니다")
        if len(self.data) == 0:
            raise ValueError("data는 비어 있을 수 없습니다")