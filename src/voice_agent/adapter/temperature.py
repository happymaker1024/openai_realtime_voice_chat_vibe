SUPPORTED = {"C", "F", "K"}   # 허용 목록: 섭씨·화씨·켈빈


def _to_celsius(value: float, unit: str) -> float:
    """어떤 단위든 일단 '섭씨'로 바꾼다(중간 기준점)."""
    if unit == "C":
        return value
    if unit == "F":
        return (value - 32) * 5 / 9      # 화씨 → 섭씨
    return value - 273.15                # 켈빈 → 섭씨


def _from_celsius(celsius: float, unit: str) -> float:
    """섭씨를 목표 단위로 바꾼다."""
    if unit == "C":
        return celsius
    if unit == "F":
        return celsius * 9 / 5 + 32       # 섭씨 → 화씨
    return celsius + 273.15               # 섭씨 → 켈빈


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """온도를 from_unit에서 to_unit으로 변환한다. 지원 밖 단위면 ValueError."""
    src = from_unit.strip().upper()       # 정규화(공백·대소문자 통일)
    dst = to_unit.strip().upper()

    # 🛡️ 허용 목록 검사.
    for unit in (src, dst):
        if unit not in SUPPORTED:
            raise ValueError(f"지원하지 않는 단위: {unit} (지원: {sorted(SUPPORTED)})")

    # 섭씨를 '가운데 기준'으로 삼아 두 단계로 변환(from → C → to).
    celsius = _to_celsius(value, src)
    if celsius < -273.15:                     # 절대영도 미만이면 거부
        raise ValueError("절대영도(-273.15°C) 미만은 불가능합니다.")
    result = _from_celsius(celsius, dst)
    return round(result, 2)