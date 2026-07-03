from dataclasses import dataclass, field

from voice_agent.domain.turn import Turn, Role

@dataclass
class Conversation:
    """여러 턴을 순서대로 담는 대화."""
    # 대화 구성 턴들의 리스트
    turns: list[Turn] = field(default_factory=list)

    def add_turn(self, turn: Turn) -> None:
        """대화 끝에 턴을 추가한다."""
        # 새로운 턴을 turns 리스트에 추가
        self.turns.append(turn)

    def last_user_text(self) -> str | None:
        """가장 최근 사용자 발화의 텍스트. 없으면 None."""
        # 뒤에서 앞으로 턴을 반복 순회
        for turn in reversed(self.turns):
            # 사용자 역할인 턴을 찾으면
            if turn.role == Role.USER:
                # 해당 턴의 텍스트 반환
                return turn.text
        # 사용자 턴이 없으면 None 반환
        return None
    

    def assistant_replies(self) -> list[str]:
        """어시스턴트가 말한 텍스트만 순서대로 모아 돌려준다."""
        # 리스트 컴프리헨션 읽는 법(뒤에서부터):
        #   self.turns 를 하나씩 turn 으로 꺼내서(for turn in self.turns)
        #   role 이 ASSISTANT 인 것만 남기고(if turn.role == Role.ASSISTANT)
        #   그 turn 의 text 를 모아 새 리스트로 만든다([turn.text ...])
        return [turn.text for turn in self.turns if turn.role == Role.ASSISTANT]