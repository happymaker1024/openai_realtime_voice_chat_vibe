from voice_agent.adapter.realtime_tools import to_realtime_tool, build_tools
from voice_agent.domain.tool_spec import ToolSpec
from voice_agent.domain.tool_toggle import ToolToggleState
from voice_agent.usecase.list_active_tools import ListActiveTools
from voice_agent.adapter.tools import TOOL_SPECS

def test_to_realtime_tool_shape():
    spec = ToolSpec(
        name="get_weather",
        description="날씨를 알려준다",
        parameters={"city": {"type": "string"}},
    )
    tool = to_realtime_tool(spec)

    # Realtime 함수 정의의 표준 모양인지 확인한다.
    assert tool["type"] == "function"
    assert tool["name"] == "get_weather"
    assert tool["description"] == "날씨를 알려준다"
    # parameters는 JSON 스키마(object) 형태로 감싸진다.
    assert tool["parameters"]["type"] == "object"
    assert tool["parameters"]["properties"] == {"city": {"type": "string"}}
    assert tool["parameters"]["required"] == ["city"]   # 인자가 있으면 필수로 표시


def test_build_tools_from_specs():
    specs = [
        ToolSpec(name="get_current_time", description="시각", parameters={}),
        ToolSpec(name="get_weather", description="날씨", parameters={"city": {"type": "string"}}),
    ]
    tools = build_tools(specs)

    assert len(tools) == 2
    assert [t["name"] for t in tools] == ["get_current_time", "get_weather"]
    # 인자 없는 도구는 properties가 비고 required도 빈 목록.
    assert tools[0]["parameters"]["properties"] == {}
    assert tools[0]["parameters"]["required"] == []


class _Registry:
    """TOOL_SPECS를 그대로 돌려주는 테스트용 레지스트리."""
    def all_specs(self):
        return TOOL_SPECS


def test_toggle_filters_tools():
    # get_weather만 켠다
    toggles = ToolToggleState()
    toggles.toggle("get_weather")

    # 켜진 명세만 골라 → Realtime 도구로 변환
    active = ListActiveTools(registry=_Registry()).execute(toggles)
    tools = build_tools(active)

    assert len(tools) == 1                     # 하나만 켰으니 하나만
    assert tools[0]["name"] == "get_weather"   # 그게 get_weather


def test_calculate_off_excludes_it():
    # 계산기만 빼고 두 도구를 켠다
    toggles = ToolToggleState()
    toggles.toggle("get_current_time")
    toggles.toggle("get_weather")

    active = ListActiveTools(registry=_Registry()).execute(toggles)
    tools = build_tools(active)
    names = [t["name"] for t in tools]

    assert "calculate" not in names        # 안 켰으니 빠져야 한다
    assert "get_weather" in names