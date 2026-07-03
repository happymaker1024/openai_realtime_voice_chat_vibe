import json

from voice_agent.adapter.tools import get_current_time, get_weather, run_tool
from voice_agent.adapter.tools import run_tool
from voice_agent.domain.rate_limiter import RateLimiter
from voice_agent.adapter.tools import rate_limit_error


def test_get_current_time_returns_string():
    # 시각 함수는 사람이 읽을 수 있는 문자열을 돌려준다(정확한 값은 실행 시각마다 다름).
    out = get_current_time()
    assert isinstance(out, str)
    assert len(out) > 0


def test_get_weather_returns_city_info():
    # 데모 날씨는 도시 이름을 담은 설명 문자열을 돌려준다.
    out = get_weather(city="서울")
    assert "서울" in out


def test_run_tool_dispatches_by_name():
    # run_tool은 이름으로 함수를 찾아 실행하고, 결과를 'JSON 문자열'로 돌려준다.
    #  (모델에 돌려줄 function_call_output이 JSON 문자열이어야 하기 때문)
    out = run_tool("get_weather", {"city": "부산"})
    parsed = json.loads(out)          # 문자열을 다시 dict로 되돌려 확인
    assert "부산" in parsed["result"]


def test_run_tool_unknown_name_is_safe():
    # 등록 안 된 이름이 와도 죽지 않고, 에러를 담은 JSON을 돌려준다.
    out = run_tool("no_such_tool", {})
    parsed = json.loads(out)
    assert "error" in parsed


def test_unknown_tool_returns_error_json():
    out = run_tool("get_horoscope", {"sign": "물병자리"})
    parsed = json.loads(out)
    assert "error" in parsed                 # 죽지 않고 에러를 담아 돌려준다
    assert "get_horoscope" in parsed["error"]


def test_calculate_tool_runs():
    out = run_tool("calculate", {"expression": "3 + 4 * 2"})
    parsed = json.loads(out)
    assert parsed["result"] == "11"          # 결과는 문자열로 담아 돌려준다


def test_run_tool_wraps_execution_error():
    # 위험한/잘못된 식이 와도 예외로 죽지 않고 error JSON을 돌려준다.
    out = run_tool("calculate", {"expression": "__import__('os')"})
    parsed = json.loads(out)
    assert "error" in parsed


def test_run_tool_rejects_missing_argument():
    # city 없이 get_weather 호출 → 실행 안 하고 에러 반환
    out = run_tool("get_weather", {})
    parsed = json.loads(out)
    assert "error" in parsed
    assert "city" in parsed["error"]


def test_divide_by_zero_is_safe():
    out = run_tool("calculate", {"expression": "1 / 0"})
    parsed = json.loads(out)
    assert "error" in parsed          # 죽지 않고 에러로 안내


def test_convert_currency_tool_runs():
    out = run_tool("convert_currency",
                   {"amount": 10, "from_currency": "USD", "to_currency": "KRW"})
    parsed = json.loads(out)
    assert "KRW" in parsed["result"] or "원" in parsed["result"]


def test_convert_currency_unsupported_is_error():
    out = run_tool("convert_currency",
                   {"amount": 1, "from_currency": "USD", "to_currency": "XYZ"})
    parsed = json.loads(out)
    assert "error" in parsed          # 허용 목록 위반 → run_tool이 에러로 감쌈


def test_rate_limit_error_none_when_allowed():
    limiter = RateLimiter(max_calls=1, window_seconds=10)
    assert rate_limit_error(limiter, "get_weather") is None   # 첫 호출은 통과


def test_rate_limit_error_when_exceeded():
    limiter = RateLimiter(max_calls=1, window_seconds=10)
    rate_limit_error(limiter, "get_weather")                  # 한도 채움
    out = rate_limit_error(limiter, "get_weather")            # 초과
    assert out is not None
    parsed = json.loads(out)
    assert "error" in parsed


class _Clock:
    def __init__(self): self.t = 0.0
    def now(self): return self.t
    def tick(self, s): self.t += s


def test_rate_limit_recovers_after_window():
    clock = _Clock()
    limiter = RateLimiter(max_calls=1, window_seconds=10, now=clock.now)

    assert rate_limit_error(limiter, "get_weather") is None    # 1번째 허용
    assert rate_limit_error(limiter, "get_weather") is not None # 2번째 초과
    clock.tick(11)                                             # 창이 지나면
    assert rate_limit_error(limiter, "get_weather") is None     # 다시 허용


def test_convert_temperature_tool_runs():
    out = run_tool("convert_temperature",
                   {"value": 100, "from_unit": "C", "to_unit": "F"})
    parsed = json.loads(out)
    assert "212" in parsed["result"]