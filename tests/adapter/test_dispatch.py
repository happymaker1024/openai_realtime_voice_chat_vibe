import json

from voice_agent.adapter.tools import dispatch_tool
from voice_agent.domain.rate_limiter import RateLimiter
import voice_agent.adapter.tools as tools_mod
from voice_agent.domain.rate_limiter import RateLimiter


def _fresh_limiter():
    # 넉넉한 한도(테스트가 빈도에 안 걸리게).
    return RateLimiter(max_calls=100, window_seconds=10)


def test_dispatch_success():
    out = dispatch_tool(_fresh_limiter(), "get_weather", {"city": "서울"})
    parsed = json.loads(out)
    assert "result" in parsed


def test_dispatch_unknown_tool():
    out = dispatch_tool(_fresh_limiter(), "no_such", {})
    assert "error" in json.loads(out)


def test_dispatch_missing_argument():
    out = dispatch_tool(_fresh_limiter(), "get_weather", {})   # city 누락
    parsed = json.loads(out)
    assert "error" in parsed
    assert "city" in parsed["error"]


def test_dispatch_policy_error():
    out = dispatch_tool(_fresh_limiter(), "convert_currency",
                        {"amount": 1, "from_currency": "USD", "to_currency": "XYZ"})
    assert "error" in json.loads(out)


def test_dispatch_rate_limited_first():
    # 한도 1로 두면, 2번째 호출은 '빈도 제한'에서 먼저 막힌다.
    limiter = RateLimiter(max_calls=1, window_seconds=10)
    assert "result" in json.loads(dispatch_tool(limiter, "get_current_time", {}))
    out = dispatch_tool(limiter, "get_current_time", {})
    parsed = json.loads(out)
    assert "error" in parsed
    assert "잦습니다" in parsed["error"]      # 빈도 제한 메시지


def test_rate_limit_short_circuits_execution(monkeypatch):
    calls = {"n": 0}

    def fake_time():
        calls["n"] += 1                 # 실제 실행되면 카운터 증가
        return "시각"

    # get_current_time을 카운터 함수로 바꿔치기(monkeypatch).
    monkeypatch.setitem(tools_mod.TOOL_HANDLERS, "get_current_time", fake_time)

    limiter = RateLimiter(max_calls=1, window_seconds=10)
    tools_mod.dispatch_tool(limiter, "get_current_time", {})   # 1번째: 실행됨(n=1)
    tools_mod.dispatch_tool(limiter, "get_current_time", {})   # 2번째: 빈도 초과 → 실행 안 됨

    assert calls["n"] == 1             # 두 번째는 함수에 닿지 않았다