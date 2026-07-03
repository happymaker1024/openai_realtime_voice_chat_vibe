from voice_agent.domain.tool_spec import ToolSpec
from voice_agent.domain.tool_toggle import ToolToggleState
from voice_agent.usecase.ports import ToolRegistryPort


class ListActiveTools:
    """토글 상태를 받아, 켜진 도구의 명세만 추려 돌려준다."""

    def __init__(self, registry: ToolRegistryPort):
        # 도구 명세들을 제공하는 레지스트리(포트)를 주입받는다(DI).
        self._registry = registry

    def execute(self, toggles: ToolToggleState) -> list[ToolSpec]:
        # 아래는 '리스트 컴프리헨션'. 세 줄을 위→아래로 이렇게 읽는다:
        #   1) self._registry.all_specs() 로 등록된 전체 도구를 꺼내
        #   2) 하나씩 spec 이라는 이름으로 돌면서
        #   3) toggles.is_enabled(spec.name) 이 참인(켜진) 것만 남겨
        #   → 남은 spec 들을 모아 새 리스트로 돌려준다.
        return [
            spec                                      # 남길 값: 도구 명세 그 자체
            for spec in self._registry.all_specs()    # 전체 도구를 하나씩
            if toggles.is_enabled(spec.name)          # 켜진 것만 통과
        ]