from dataclasses import dataclass


@dataclass(frozen=True)  # 설정값은 한 세션 동안 바뀌지 않으므로 불변으로
class SessionConfig:
    """보이스 세션을 시작할 때 쓰는 설정값 묶음."""

    # 아래는 모두 '기본값(= 뒤의 값)'을 가진 필드.
    # 호출 시 생략하면 이 기본값이 자동으로 쓰인다.
    model: str = "gpt-realtime"     # 접근성 넓은 GA 실시간 모델 (대부분 계정에서 바로 사용 가능)
    voice: str = "alloy"            # 합성 음성 종류 (실제 사용 가능한 이름은 4교시 어댑터에서 검증)
    reasoning_effort: str = "low"   # 추론 강도. low=빠르고 저렴 → 비용 가드의 핵심