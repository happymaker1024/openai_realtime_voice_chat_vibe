import time                                   # 기본 시계로 쓸 표준 라이브러리
from collections.abc import Callable


class RateLimiter:
    """최근 window_seconds 안에 max_calls번까지만 허용하는 빈도 제한기."""

    def __init__(self, max_calls: int, window_seconds: float,
                 now: Callable[[], float] = time.monotonic):
        # now: '현재 시각'을 주는 함수. 테스트에선 가짜 시계를 주입한다(DI).
        #  기본값 time.monotonic은 뒤로 안 가는(단조 증가) 시계라 측정에 안전.
        self._max = max_calls
        self._window = window_seconds
        self._now = now
        # key(도구 이름) → 호출 시각 목록. 도구마다 따로 센다.
        self._calls: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        """이번 호출을 허용하면 True(그리고 기록), 한도 초과면 False."""
        t = self._now()
        # 이 key의 과거 호출 중, 창(window) 안에 드는 것만 남긴다(오래된 건 버림).
        recent = [c for c in self._calls.get(key, []) if t - c < self._window]
        # 창 안 호출이 이미 한도에 도달했으면 거부(기록은 갱신만 하고 추가 안 함).
        if len(recent) >= self._max:
            self._calls[key] = recent
            return False
        # 아직 여유가 있으면 이번 호출 시각을 남기고 허용.
        recent.append(t)
        self._calls[key] = recent
        return True