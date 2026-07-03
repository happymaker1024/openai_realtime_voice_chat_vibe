from dataclasses import dataclass   # 데이터 보관용 클래스를 짧게 정의하는 표준 도구
from enum import Enum               # 정해진 선택지만 허용하는 '열거형'을 만드는 표준 도구

from voice_agent.domain.audio_frame import AudioFrame


class Role(str, Enum):
    """발화 주체: 사용자 또는 어시스턴트.

    (str, Enum)을 함께 상속하면 '문자열이면서 선택지'가 된다.
    → Role.USER == "user" 처럼 문자열로도 비교할 수 있어 편리하다.
    """
    USER = "user"            # 사용자의 발화를 나타내는 선택지
    ASSISTANT = "assistant"  # 어시스턴트의 발화를 나타내는 선택지


@dataclass(frozen=True)   # frozen=True: 한 번 만들면 값을 못 바꾸는 불변 객체로
class Turn:
    """대화의 한 턴(발화 한 번)."""
    role: Role   # 이 발화의 주체 (Role.USER 또는 Role.ASSISTANT)
    text: str    # 이 발화의 내용(문자열)
    # ↑ @dataclass가 위 두 필드를 받는 __init__을 자동으로 만들어 준다.
    #   그래서 Turn(role=..., text=...) 형태로 바로 생성할 수 있다.

    audio: AudioFrame | None = None