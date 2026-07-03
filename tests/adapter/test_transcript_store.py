from pathlib import Path

from voice_agent.adapter.transcript_store import render_markdown, FileTranscriptStore
from voice_agent.domain.conversation import Conversation
from voice_agent.domain.turn import Turn, Role


def _sample():
    c = Conversation()
    c.add_turn(Turn(role=Role.USER, text="안녕"))
    c.add_turn(Turn(role=Role.ASSISTANT, text="안녕하세요!"))
    return c


def test_render_markdown_contains_turns():
    md = render_markdown(_sample())
    assert "안녕하세요!" in md
    assert "사용자" in md or "user" in md.lower()


def test_saves_file(tmp_path):
    store = FileTranscriptStore(directory=str(tmp_path))
    store.save("sess-1", _sample())

    saved = Path(tmp_path) / "sess-1.md"
    assert saved.exists()
    assert "안녕하세요!" in saved.read_text(encoding="utf-8")


def test_sanitizes_session_id(tmp_path):
    store = FileTranscriptStore(directory=str(tmp_path))
    # 경로 주입 시도: 위험 문자는 제거되어 tmp_path 밖으로 못 나간다.
    store.save("../../evil", _sample())

    # 상위로 탈출한 파일이 생기지 않았다.
    assert not (Path(tmp_path).parent / "evil.md").exists()
    # tmp_path 안에 정규화된 이름으로 저장됐다.
    assert list(Path(tmp_path).glob("*.md"))
