import json                                  # 결과를 JSON 문자열로 만들기 위해
from datetime import datetime                # 실제 현재 시각을 얻기 위해

from voice_agent.domain.tool_spec import ToolSpec   # 도구 명세(2교시 값객체)
from voice_agent.adapter.safe_math import safe_calculate 

from voice_agent.domain.tool_guard import check_required
from voice_agent.adapter.currency import convert_currency as _convert 

from voice_agent.domain.rate_limiter import RateLimiter
from voice_agent.adapter.temperature import convert_temperature as _convert_temp
from voice_agent.adapter.length import convert_length as _convert_length



def get_current_time() -> str:
    """지금 시각을 사람이 읽는 문자열로 돌려준다(예: '오후 3시 12분')."""
    now = datetime.now()                     # 실행 순간의 실제 시각
    return now.strftime("%p %I시 %M분")       # %p=오전/오후, %I=12시간제 시, %M=분


def get_weather(city: str) -> str:
    """(데모) 주어진 도시의 날씨를 돌려준다. 실제 API 대신 고정 문구를 쓴다."""
    # 실제 서비스라면 여기서 날씨 API를 호출한다(선택 미션에서 교체).
    return f"{city}의 날씨는 맑고 기온은 22도입니다. (데모 데이터)"


def calculate(expression: str) -> str:
    """수식을 안전하게 계산해 결과를 문자열로 돌려준다."""
    value = safe_calculate(expression)       # 허용 안 된 식이면 여기서 ValueError
    # 3.0처럼 정수로 떨어지면 소수점을 떼서 깔끔하게(11.0 → "11").
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def convert_currency_tool(amount: float, from_currency: str, to_currency: str) -> str:
    """환율 변환 결과를 사람이 읽는 문자열로 돌려준다."""
    value = _convert(amount, from_currency, to_currency)   # 지원 밖이면 ValueError
    return f"{amount} {from_currency.upper()} = {value} {to_currency.upper()}"


def convert_temperature_tool(value: float, from_unit: str, to_unit: str) -> str:
    result = _convert_temp(value, from_unit, to_unit)          # 지원 밖이면 ValueError
    return f"{value}°{from_unit.upper()} = {result}°{to_unit.upper()}"


def convert_length_tool(value: float, from_unit: str, to_unit: str) -> str:
    """길이 변환 결과를 사람이 읽는 문자열로 돌려준다."""
    result = _convert_length(value, from_unit, to_unit)        # 지원 밖·음수면 ValueError
    return f"{value} {from_unit} = {result} {to_unit}"


# 이름 → 실제 함수 로 이어주는 표. run_tool이 여기서 함수를 찾아 부른다.
TOOL_HANDLERS = {
    "get_current_time": get_current_time,
    "get_weather": get_weather,
    "calculate": calculate,
    "convert_currency": convert_currency_tool,
    "convert_temperature": convert_temperature_tool,
    "convert_length": convert_length_tool,
}

# 모델에게 알려줄 '도구 명세' 목록. name/description/parameters로 구성.
#  - description: 모델이 '언제 이 도구를 쓸지' 판단하는 근거.
#  - parameters: 입력 형식(여기선 property 이름 → 타입).
TOOL_SPECS = [
    ToolSpec(
        name="get_current_time",
        description="현재 시각을 알려준다. 사용자가 지금 몇 시인지 물을 때 사용.",
        parameters={},                       # 입력 없음
    ),
    ToolSpec(
        name="get_weather",
        description="특정 도시의 현재 날씨를 알려준다. 날씨를 물을 때 사용.",
        parameters={"city": {"type": "string"}},   # city: 문자열 하나
    ),
    ToolSpec(
        name="calculate",
        description="사칙연산 수식을 계산한다. 사용자가 계산을 요청할 때 사용.",
        parameters={"expression": {"type": "string"}},
    ),
    ToolSpec(
        name="convert_currency",
        description="통화를 환전한다. 지원: KRW, USD, JPY, EUR. 환율/환전 요청 시 사용.",
        parameters={
            "amount": {"type": "number"},
            "from_currency": {"type": "string"},
            "to_currency": {"type": "string"},
        },
    ),
    ToolSpec(
        name="convert_temperature",
        description="온도를 변환한다. 지원: C(섭씨), F(화씨), K(켈빈). 온도 변환 요청 시 사용.",
        parameters={
            "value": {"type": "number"},
            "from_unit": {"type": "string"},
            "to_unit": {"type": "string"},
        },
    ),
    ToolSpec(
        name="convert_length",
        description="길이를 변환한다. 지원: m, km, cm, mi(마일). 길이/거리 변환 요청 시 사용.",
        parameters={
            "value": {"type": "number"},
            "from_unit": {"type": "string"},
            "to_unit": {"type": "string"},
        },
    ),
]


# 이름 → 명세. 검증(check_required)에 쓴다.
_SPEC_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}


def run_tool(name: str, arguments: dict) -> str:
    """이름으로 함수를 찾아 arguments로 실행하고, 결과를 JSON 문자열로 돌려준다."""
    handler = TOOL_HANDLERS.get(name)        # 이름에 해당하는 함수 찾기
    if handler is None:                      # 없으면 에러를 담아 안전하게 반환
        return json.dumps({"error": f"unknown tool: {name}"}, ensure_ascii=False)
    
    # 🛡️ 가드레일: 실행 전에 필수 인자를 검증한다.
    spec = _SPEC_BY_NAME.get(name)
    if spec is not None:
        errors = check_required(spec, arguments)
        if errors:                                       # 하나라도 위반이면
            return json.dumps({"error": "; ".join(errors)}, ensure_ascii=False)
    
    # arguments(dict)를 함수의 키워드 인자로 풀어 호출한다(**arguments).
    #  예: {"city": "부산"} → handler(city="부산")
    try:
        result = handler(**arguments)                    # 실제 실행
    except (ValueError, TypeError, ZeroDivisionError) as exc:               # 검증 실패·잘못된 인자 등
        # 예외로 루프가 죽지 않게, 에러를 결과로 감싸 모델에 돌려준다.
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
    # 모델에 돌려줄 결과는 JSON 문자열이어야 하므로 감싼다.
    #  ensure_ascii=False: 한글이 \uXXXX로 깨지지 않게.
    return json.dumps({"result": result}, ensure_ascii=False)


def rate_limit_error(limiter: RateLimiter, name: str) -> str | None:
    """호출이 허용되면 None, 초과면 안내용 에러 JSON을 돌려준다."""
    if limiter.allow(name):        # 허용되면 통과(내부에 이번 호출 기록됨)
        return None
    return json.dumps(
        {"error": f"요청이 너무 잦습니다. 잠시 후 다시 시도하세요: {name}"},
        ensure_ascii=False,
    )


def dispatch_tool(limiter, name: str, arguments: dict) -> str:
    """가드레일 파이프라인: 빈도 → (존재 → 인자 → 실행)을 순서대로 통과시킨다."""
    # 1) 빈도 제한 — 가장 싼 거부를 맨 앞에. 초과면 즉시 중단.
    denied = rate_limit_error(limiter, name)
    if denied is not None:
        return denied
    # 2~4) 존재 확인 · 인자 검증 · 실행은 run_tool이 이미 순서대로 처리한다.
    return run_tool(name, arguments)