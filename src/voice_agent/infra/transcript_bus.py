import asyncio

_subscribers: list[asyncio.Queue] = []


def publish(text: str) -> None:
    """모든 구독자에게 자막 한 조각을 보낸다."""
    for q in _subscribers:
        q.put_nowait(text)


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    if q in _subscribers:
        _subscribers.remove(q)