from voice_agent.domain.conversation import Conversation
from voice_agent.domain.turn import Role


def summarize(conversation: Conversation) -> str:
    """대화를 한 줄로 요약한다(순수 규칙, 외부 의존 없음)."""
    turns = conversation.turns
    if not turns:
        return "빈 대화"
    # 첫 사용자 발화를 찾아 미리보기(30자)로.
    first_user = next((t.text for t in turns if t.role == Role.USER), "")
    preview = first_user[:30] + ("…" if len(first_user) > 30 else "")
    return f"{len(turns)}개 턴 · 시작: {preview}"
