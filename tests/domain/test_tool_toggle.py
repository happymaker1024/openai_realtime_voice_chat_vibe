from voice_agent.domain.tool_toggle import ToolToggleState


def test_new_state_has_nothing_enabled():
    """새로운 상태에서는 모든 도구가 비활성화되어 있는지 확인"""
    state = ToolToggleState()
    assert state.is_enabled("weather") is False


def test_toggle_turns_on_then_off():
    """토글 기능이 도구를 켜고 끌 수 있는지 확인"""
    state = ToolToggleState()

    state.toggle("weather")      # 켜기
    assert state.is_enabled("weather") is True

    state.toggle("weather")      # 다시 끄기
    assert state.is_enabled("weather") is False


def test_multiple_tools_independent():
    """여러 도구들이 독립적으로 관리되는지 확인"""
    state = ToolToggleState()
    state.toggle("weather")
    state.toggle("search")

    assert state.is_enabled("weather") is True
    assert state.is_enabled("search") is True
    assert state.is_enabled("booking") is False