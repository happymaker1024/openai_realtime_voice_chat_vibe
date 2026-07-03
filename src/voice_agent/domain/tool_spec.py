from dataclasses import dataclass, field
from typing import Any  # "아무 타입이나"를 뜻하는 표기. 파라미터 스펙 값이 자유로워서 사용


@dataclass(frozen=True)  # frozen: 한 번 정의한 도구 명세는 바뀌지 않음(불변)
class ToolSpec:
    """에이전트가 호출할 수 있는 '도구 하나'의 명세(설명서)."""

    name: str          # 도구 이름. 모델이 이 이름으로 도구를 지목한다 (예: "weather")
    description: str   # 도구 설명. 모델이 '언제 이 도구를 쓸지' 판단하는 근거가 된다

    # 파라미터 스펙: { "인자이름": { "type": "string" ... } } 형태의 dict.
    # default_factory=dict → 객체를 만들 때마다 '새 빈 dict'를 준다 (리스트 때와 같은 공유 버그 방지)
    parameters: dict[str, Any] = field(default_factory=dict)