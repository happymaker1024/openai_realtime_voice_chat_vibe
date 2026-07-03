import pytest

from voice_agent.adapter.safe_math import safe_calculate


def test_basic_arithmetic():
    assert safe_calculate("3 + 4") == 7
    assert safe_calculate("10 - 2 * 3") == 4          # 곱셈 먼저(연산 우선순위)
    assert safe_calculate("(1 + 2) * 3") == 9         # 괄호 우선


def test_division_and_negative():
    assert safe_calculate("9 / 2") == 4.5
    assert safe_calculate("-5 + 2") == -3


def test_rejects_names_and_calls():
    # 이름(변수/함수)이나 호출이 들어오면 '허용되지 않은 식'으로 거부한다.
    with pytest.raises(ValueError):
        safe_calculate("__import__('os')")
    with pytest.raises(ValueError):
        safe_calculate("abs(-3)")
    with pytest.raises(ValueError):
        safe_calculate("x + 1")


def test_rejects_garbage():
    with pytest.raises(ValueError):
        safe_calculate("3 +")        # 문법 오류도 안전하게 ValueError로