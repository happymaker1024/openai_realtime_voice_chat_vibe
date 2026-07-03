from voice_agent.domain.tool_spec import ToolSpec


def test_tool_spec_holds_name_and_description():
    # 이름과 설명만으로 ToolSpec을 만들 수 있어야 한다
    spec = ToolSpec(name="weather", description="도시의 날씨를 물어볼 때, 도시의 현재 날씨를 알려준다")

    assert spec.name == "weather"                    # 이름이 그대로 보관되는가
    assert spec.description == "도시의 날씨를 물어볼 때, 도시의 현재 날씨를 알려준다"  # 설명이 그대로 보관되는가
    assert spec.parameters == {}                     # 파라미터를 안 주면 빈 dict가 기본


def test_tool_spec_holds_parameters():
    # 파라미터 스펙(JSON 스키마 형태)도 담을 수 있어야 한다
    spec = ToolSpec(
        name="weather",
        description="날씨 조회",
        parameters={"city": {"type": "string"}},     # city는 문자열 입력이라는 스펙
    )

    # 중첩된 dict 안의 값까지 잘 들어갔는지 확인
    assert spec.parameters["city"]["type"] == "string"