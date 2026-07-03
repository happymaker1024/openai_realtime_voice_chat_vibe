from voice_agent.domain.tool_spec import ToolSpec   # 변환할 도구 명세


def to_realtime_tool(spec: ToolSpec) -> dict:
    """ToolSpec 하나를 Realtime 함수 정의 JSON(dict)으로 바꾼다."""
    return {
        "type": "function",              # 이 도구가 '함수형'임을 표시
        "name": spec.name,               # 모델이 지목할 함수 이름
        "description": spec.description,  # 모델이 '언제 쓸지' 판단할 설명
        "parameters": {                  # 입력 형식을 JSON 스키마로
            "type": "object",            # 인자들은 object(키-값) 형태
            "properties": spec.parameters,          # 각 인자의 이름·타입
            "required": list(spec.parameters.keys()),  # 정의된 인자는 모두 필수로
        },
    }


def build_tools(specs: list[ToolSpec]) -> list[dict]:
    """도구 명세 목록 전체를 Realtime 함수 정의 목록으로 바꾼다."""
    # 각 spec을 to_realtime_tool로 변환해 리스트로 모은다.
    return [to_realtime_tool(spec) for spec in specs]