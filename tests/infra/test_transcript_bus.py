from voice_agent.infra import transcript_bus


def test_publish_reaches_subscriber():
    q = transcript_bus.subscribe()
    transcript_bus.publish("안녕")
    assert q.get_nowait() == "안녕"
    transcript_bus.unsubscribe(q)


def test_unsubscribe_stops_delivery():
    q = transcript_bus.subscribe()
    transcript_bus.unsubscribe(q)
    transcript_bus.publish("여기")
    assert q.empty()