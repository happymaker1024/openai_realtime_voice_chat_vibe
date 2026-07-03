from voice_agent.domain.conversation import Conversation
from voice_agent.domain.summary import summarize
from voice_agent.usecase.ports import SummarizerPort, TranscriptStorePort


class SaveConversation:
    """대화를 저장하고 요약을 돌려준다. 마크다운·파일·모델은 모른다(포트에 위임)."""

    def __init__(self, store: TranscriptStorePort, summarizer: SummarizerPort | None = None):
        self._store = store
        self._summarizer = summarizer

    def execute(self, conversation: Conversation, session_id: str) -> str:
        self._store.save(session_id, conversation)   # 어떻게 저장할지는 어댑터 몫
        return self._summarize(conversation)

    def _summarize(self, conversation: Conversation) -> str:
        if self._summarizer is not None:
            try:
                return self._summarizer.summarize(conversation)
            except Exception:
                pass   # 모델 요약 실패 → 도메인 규칙 기반 요약으로 폴백
        return summarize(conversation)
