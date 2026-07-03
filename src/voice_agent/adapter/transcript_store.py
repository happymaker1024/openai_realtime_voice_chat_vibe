from pathlib import Path

from voice_agent.domain.conversation import Conversation
from voice_agent.domain.turn import Role


def render_markdown(conversation: Conversation) -> str:
    """대화를 마크다운 문자열로 만든다(표현 관심사 → 어댑터)."""
    lines = ["# 대화 기록", ""]
    for turn in conversation.turns:
        who = "🧑 사용자" if turn.role == Role.USER else "🤖 어시스턴트"
        lines.append(f"**{who}**: {turn.text}")
    return "\n".join(lines)


class FileTranscriptStore:
    """대화를 파일로 저장하는 어댑터. TranscriptStorePort 약속을 만족한다."""

    def __init__(self, directory: str):
        self._dir = Path(directory)

    def save(self, session_id: str, conversation: Conversation) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)         # 폴더 없으면 생성
        # 🛡️ 경로 주입 방지: 파일 이름엔 안전한 문자만 남긴다.
        safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "session"
        path = self._dir / f"{safe}.md"                      # 항상 지정 폴더 '안'
        path.write_text(render_markdown(conversation), encoding="utf-8")
