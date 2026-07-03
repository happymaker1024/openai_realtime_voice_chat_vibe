from voice_agent.adapter.function_call import extract_function_call


def test_extracts_function_call():
    # 실제 done 이벤트: name/call_id/arguments(JSON '문자열')를 담고 온다.
    event = {
        "type": "response.function_call_arguments.done",
        "name": "get_weather",
        "call_id": "call_abc",
        "arguments": '{"city": "서울"}',
    }
    fc = extract_function_call(event)

    assert fc is not None
    assert fc["name"] == "get_weather"
    assert fc["call_id"] == "call_abc"
    # arguments 문자열이 dict로 '파싱'되어 나온다.
    assert fc["arguments"] == {"city": "서울"}


def test_returns_none_for_other_events():
    assert extract_function_call({"type": "response.output_audio.delta"}) is None
    assert extract_function_call({"type": "response.done"}) is None


def test_handles_empty_arguments():
    # 인자 없는 함수(get_current_time)는 arguments가 빈 문자열/누락일 수 있다 → 빈 dict.
    event = {
        "type": "response.function_call_arguments.done",
        "name": "get_current_time",
        "call_id": "call_xyz",
        "arguments": "",
    }
    fc = extract_function_call(event)
    assert fc["arguments"] == {}