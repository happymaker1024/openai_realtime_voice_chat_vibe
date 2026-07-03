# 데모 환율표: '1 USD = 각 통화 값'. 실제 서비스라면 환율 API로 대체한다.
_RATES = {
    "USD": 1.0,
    "KRW": 1400.0,
    "JPY": 150.0,
    "EUR": 0.92,
}

# 허용 목록(allowlist): 우리가 지원하는 통화 집합. 표의 키가 곧 허용 목록이다.
SUPPORTED = set(_RATES.keys())


def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """amount를 from_currency에서 to_currency로 변환한다. 지원 통화가 아니면 ValueError."""
    if amount <= 0:
        raise ValueError("금액은 0보다 커야 합니다.")
    
    # 대소문자·공백 차이를 없애 비교(예: ' usd ' → 'USD').
    src = from_currency.strip().upper()
    dst = to_currency.strip().upper()

    # 🛡️ 허용 목록 검사: 둘 중 하나라도 지원 밖이면 거부.
    for code in (src, dst):
        if code not in SUPPORTED:
            raise ValueError(f"지원하지 않는 통화: {code} (지원: {sorted(SUPPORTED)})")

    # USD를 기준으로 환산: from → USD → to.
    #  amount(from) ÷ from레이트 = USD, × to레이트 = to.
    usd = amount / _RATES[src]
    result = usd * _RATES[dst]
    # 소수 둘째 자리로 반올림(금액 표시에 적당).
    return round(result, 2)