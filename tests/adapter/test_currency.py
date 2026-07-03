import pytest

from voice_agent.adapter.currency import convert_currency, SUPPORTED


def test_supported_set():
    # 허용 목록에 기대한 통화들이 있다.
    assert {"KRW", "USD", "JPY", "EUR"} <= SUPPORTED


def test_converts_between_currencies():
    # 1 USD를 KRW로 (데모 환율 기준). 대략적인 값이라 범위로 확인.
    krw = convert_currency(amount=1, from_currency="USD", to_currency="KRW")
    assert 1000 <= krw <= 2000


def test_same_currency_is_identity():
    assert convert_currency(amount=100, from_currency="USD", to_currency="USD") == 100


def test_rejects_unsupported_currency():
    # 허용 목록에 없는 통화는 ValueError로 거부한다(대소문자 무관하게 정규화).
    with pytest.raises(ValueError):
        convert_currency(amount=1, from_currency="USD", to_currency="XYZ")


def test_rejects_non_positive_amount():
    with pytest.raises(ValueError):
        convert_currency(amount=0, from_currency="USD", to_currency="KRW")
    with pytest.raises(ValueError):
        convert_currency(amount=-5, from_currency="USD", to_currency="KRW")