from voice_agent.domain.tool_spec import ToolSpec   # 검사 기준이 되는 명세


def check_required(spec: ToolSpec, arguments: dict) -> list[str]:
    """명세가 요구하는 인자가 arguments에 '있고 비어 있지 않은지' 검사한다.

    문제가 없으면 빈 목록, 있으면 사람이 읽는 오류 메시지 목록을 돌려준다.
    """
    errors: list[str] = []
    # 명세의 parameters에 적힌 인자 이름들을 하나씩 확인한다.
    for name in spec.parameters:
        value = arguments.get(name)                 # 넘어온 값(없으면 None)
        # None 이거나, 문자열인데 공백만 있으면 '빠졌다'고 본다.
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"필수 인자 누락: {name}")
    return errors