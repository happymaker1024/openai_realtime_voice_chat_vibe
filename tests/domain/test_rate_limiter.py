from voice_agent.domain.rate_limiter import RateLimiter


class FakeClock:
    """테스트용 가짜 시계. tick()으로 시간을 앞으로 돌린다."""
    def __init__(self):
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def tick(self, seconds: float) -> None:
        self.t += seconds


def test_allows_up_to_limit():
    clock = FakeClock()
    limiter = RateLimiter(max_calls=2, window_seconds=10, now=clock.now)

    assert limiter.allow("weather") is True    # 1번째 허용
    assert limiter.allow("weather") is True    # 2번째 허용
    assert limiter.allow("weather") is False   # 3번째는 창 안 초과 → 거부


def test_separate_keys_are_independent():
    clock = FakeClock()
    limiter = RateLimiter(max_calls=1, window_seconds=10, now=clock.now)

    assert limiter.allow("weather") is True
    assert limiter.allow("weather") is False   # weather는 한도 참
    assert limiter.allow("time") is True        # time은 별개로 셈


def test_resets_after_window_passes():
    clock = FakeClock()
    limiter = RateLimiter(max_calls=1, window_seconds=10, now=clock.now)

    assert limiter.allow("weather") is True
    assert limiter.allow("weather") is False
    clock.tick(11)                              # 창(10초)이 지나면
    assert limiter.allow("weather") is True     # 오래된 기록이 빠져 다시 허용