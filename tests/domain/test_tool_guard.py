from voice_agent.domain.tool_guard import check_required
from voice_agent.domain.tool_spec import ToolSpec


def test_no_errors_when_all_present():
    spec = ToolSpec(name="get_weather", description="날씨",
                    parameters={"city": {"type": "string"}})
    errors = check_required(spec, {"city": "서울"})
    assert errors == []                       # 문제 없음 → 빈 목록


def test_reports_missing_argument():
    spec = ToolSpec(name="get_weather", description="날씨",
                    parameters={"city": {"type": "string"}})
    errors = check_required(spec, {})         # city가 없음
    assert len(errors) == 1
    assert "city" in errors[0]


def test_reports_empty_value():
    spec = ToolSpec(name="get_weather", description="날씨",
                    parameters={"city": {"type": "string"}})
    errors = check_required(spec, {"city": "   "})   # 공백만 → 빈 값 취급
    assert len(errors) == 1


def test_no_params_no_errors():
    spec = ToolSpec(name="get_current_time", description="시각", parameters={})
    assert check_required(spec, {}) == []     # 인자가 필요 없으면 항상 통과