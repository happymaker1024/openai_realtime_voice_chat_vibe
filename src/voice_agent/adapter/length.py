# 각 단위의 '1개'가 몇 미터인지(미터를 허브로 삼아 변환).
_TO_METER = {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "mi": 1609.344,
}

SUPPORTED = set(_TO_METER.keys())   # 허용 목록: m, km, cm, mi


def convert_length(value: float, from_unit: str, to_unit: str) -> float:
    """value를 from_unit에서 to_unit으로 변환한다. 지원 밖 단위·음수 길이면 ValueError."""
    if value < 0:
        raise ValueError("길이는 0 이상이어야 합니다.")

    # 대소문자·공백 차이를 없애 비교(예: ' KM ' → 'km').
    src = from_unit.strip().lower()
    dst = to_unit.strip().lower()

    # 🛡️ 허용 목록 검사: 둘 중 하나라도 지원 밖이면 거부.
    for unit in (src, dst):
        if unit not in SUPPORTED:
            raise ValueError(f"지원하지 않는 단위: {unit} (지원: {sorted(SUPPORTED)})")

    # 미터를 기준으로 환산: from → m → to.
    meters = value * _TO_METER[src]
    result = meters / _TO_METER[dst]
    return round(result, 4)
