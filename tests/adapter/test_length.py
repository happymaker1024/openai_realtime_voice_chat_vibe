import pytest

from voice_agent.adapter.length import convert_length, SUPPORTED


def test_supported_units():
    assert SUPPORTED == {"m", "km", "cm", "mi"}


def test_km_to_m():
    # 3km = 3000m
    assert convert_length(value=3, from_unit="km", to_unit="m") == 3000.0


def test_m_to_km():
    # 3000m = 3km
    assert convert_length(value=3000, from_unit="m", to_unit="km") == 3.0


def test_same_unit_is_identity():
    assert convert_length(value=5, from_unit="m", to_unit="m") == 5


def test_rejects_unsupported_unit():
    with pytest.raises(ValueError):
        convert_length(value=1, from_unit="m", to_unit="yd")


def test_rejects_negative_length():
    with pytest.raises(ValueError):
        convert_length(value=-1, from_unit="m", to_unit="km")


def test_mi_to_m_to_mi_roundtrip():
    # 1mi ≈ 1609.34m 기준, 왕복 변환해도 오차 0.01 이내여야 한다.
    meters = convert_length(value=1, from_unit="mi", to_unit="m")
    assert abs(meters - 1609.34) < 0.01
    back = convert_length(value=meters, from_unit="m", to_unit="mi")
    assert abs(back - 1) < 0.01


def test_cm_to_m():
    # 250cm = 2.5m
    assert convert_length(value=250, from_unit="cm", to_unit="m") == 2.5
