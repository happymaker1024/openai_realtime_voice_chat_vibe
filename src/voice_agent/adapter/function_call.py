import json   # arguments(JSON 문자열)를 dict로 파싱


def extract_function_call(event: dict) -> dict | None:
    """함수 호출 완료 이벤트면 {name, call_id, arguments(dict)}를, 아니면 None."""
    # 1) 함수 호출 완료 이벤트가 아니면 관심 밖 → None.
    if event.get("type") != "response.function_call_arguments.done":
        return None
    # 2) arguments는 JSON '문자열'. 비어 있으면 빈 dict로 시작.
    raw = event.get("arguments") or ""
    arguments = json.loads(raw) if raw else {}   # 문자열 → dict
    # 3) 실행에 필요한 세 가지를 묶어 돌려준다.
    return {
        "name": event.get("name"),        # 부를 함수 이름
        "call_id": event.get("call_id"),  # 결과를 이어붙일 영수증 번호
        "arguments": arguments,           # 함수에 넘길 인자(dict)
    }