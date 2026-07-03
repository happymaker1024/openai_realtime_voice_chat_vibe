from voice_agent.domain.tool_spec import ToolSpec
from voice_agent.domain.tool_toggle import ToolToggleState
from voice_agent.usecase.list_active_tools import ListActiveTools


class FakeToolRegistry:
    """테스트용 가짜 레지스트리. 고정된 도구 목록을 돌려준다."""

    def __init__(self, specs):
        self._specs = specs

    def all_specs(self):
        return self._specs


def test_only_enabled_tools_are_returned():
    # 두 개의 도구가 등록돼 있고
    registry = FakeToolRegistry([
        ToolSpec(name="weather", description="날씨"),
        ToolSpec(name="search", description="검색"),
    ])
    # 토글로 'weather'만 켠 상태
    toggles = ToolToggleState()
    toggles.toggle("weather")

    usecase = ListActiveTools(registry=registry)
    active = usecase.execute(toggles)

    # 켜진 'weather'만 나와야 한다
    assert [spec.name for spec in active] == ["weather"]