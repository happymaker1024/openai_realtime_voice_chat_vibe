import pytest

from voice_agent.adapter.temperature import convert_temperature, SUPPORTED


def test_supported_units():
    assert SUPPORTED == {"C", "F", "K"}


def test_celsius_to_fahrenheit():
    # 0°C = 32°F
    assert convert_temperature(value=0, from_unit="C", to_unit="F") == 32


def test_fahrenheit_to_celsius():
    # 212°F = 100°C
    assert convert_temperature(value=212, from_unit="F", to_unit="C") == 100


def test_celsius_to_kelvin():
    # 0°C = 273.15K
    assert convert_temperature(value=0, from_unit="C", to_unit="K") == 273.15


def test_rejects_unsupported_unit():
    with pytest.raises(ValueError):
        convert_temperature(value=0, from_unit="C", to_unit="X")


def test_rejects_below_absolute_zero():
    with pytest.raises(ValueError):
        convert_temperature(value=-500, from_unit="C", to_unit="K")   # -500°C는 0K 미만