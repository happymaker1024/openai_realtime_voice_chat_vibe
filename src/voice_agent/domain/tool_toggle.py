from dataclasses import dataclass, field


@dataclass
class ToolToggleState:
    """현재 켜져 있는 도구 이름들의 집합."""
    # 활성화된 도구 이름들을 저장하는 집합
    enabled: set[str] = field(default_factory=set)

    def toggle(self, name: str) -> None:
        """켜져 있으면 끄고, 꺼져 있으면 켠다."""
        # 도구가 이미 활성화되어 있으면 제거
        if name in self.enabled:
            self.enabled.discard(name)
        # 도구가 비활성화되어 있으면 추가
        else:
            self.enabled.add(name)

    def is_enabled(self, name: str) -> bool:
        # 도구가 활성화 상태인지 확인
        return name in self.enabled