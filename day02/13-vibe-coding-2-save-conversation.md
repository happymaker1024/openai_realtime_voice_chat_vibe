# 13교시 — 바이브 코딩 ②: 큰 기능(대화 저장 + 요약)을 규율로

> **이 교시가 끝나면** "세션이 끝나면 대화를 파일로 저장하고 요약을 남기는" **여러 계층에 걸친 기능**을 바이브 코딩으로 완성합니다. 12교시의 도구 추가는 정해진 패턴을 따랐지만, 이번엔 **새 포트·유즈케이스·어댑터·인프라**를 함께 만들어야 해서, 스펙·테스트·리뷰의 규율이 훨씬 크게 작동합니다.

---

## 0. 이 교시에 만드는 것 (한눈에)

12교시는 기존 도구 패턴을 복제했습니다. 이번엔 **새로운 세로줄**(도메인→유즈케이스→포트→어댑터→인프라)을 하나 세웁니다. 템플릿이 없을수록, AI가 계층을 헷갈리기 쉬우므로 **경계를 스펙과 리뷰로 못박습니다.**

```
세션 진행 중: 어시스턴트 자막을 모아 Conversation(2교시)에 턴으로 쌓기
세션 종료 시(shutdown):
   SaveConversation(유즈케이스)
      → TranscriptStorePort.save(session_id, conversation)   ← 포트(약속)
           └─ FileTranscriptStore: 마크다운으로 렌더 → 파일로 저장  ← 어댑터
      → summarize(conversation)(도메인)로 요약 문자열 반환 → 터미널 출력
```

핵심 설계 판단: **렌더링(마크다운 만들기)은 어댑터**, **요약(턴 세기·미리보기)은 도메인**, **저장 지휘는 유즈케이스**. 유즈케이스는 포트와 도메인만 알고, 파일·마크다운은 모릅니다.

> ⚠️ **큰 기능일수록 경계가 흔들린다**: AI에게 "저장 기능 만들어줘"라고만 하면, 유즈케이스가 파일을 직접 쓰거나 도메인이 마크다운을 아는 식으로 계층이 무너지기 쉽습니다. 스펙에 **배치**를 명시하고, 리뷰로 확인합니다.

---

## 🧭 잠깐, 배경지식

이 교시에서 새로 신경 쓸 세 가지를 짚습니다.

**① 새 포트(port)를 여는 감각.** 3·4교시에서 포트를 배웠습니다. "저장"처럼 **바깥 세계(파일·DB)**와 닿는 기능은 새 포트를 엽니다. 유즈케이스는 `TranscriptStorePort`라는 약속에만 기대고, 실제 저장(파일이냐 DB냐)은 어댑터가 정합니다. 나중에 파일→클라우드로 바꿔도 유즈케이스는 그대로입니다.

**② 부수효과(side effect)와 안전.** 파일 쓰기는 **부수효과**입니다 — 실패할 수 있고(디스크 가득·권한), 실패가 대화 전체를 망치면 안 됩니다. 저장 실패는 **조용히 로그로** 남기고 세션은 정상 종료시키는 게 안전합니다(5·6교시의 "종료는 정상" 감각과 같은 결).

**③ 경로 주입(path injection)도 가드레일 대상.** `session_id`가 파일 이름이 되면, `../../etc/passwd` 같은 값이 오면 위험합니다(9~11교시의 신뢰 경계). 파일 이름에 쓰기 전 **정규화(허용 문자만 남기기)**로 막습니다. 가드레일 사고방식이 여기서도 이어집니다.

**④ 바이브 코딩 규율은 그대로.** 12교시의 다섯 원칙(규칙 파일 → 스펙 → 테스트 먼저 → 구현 → 리뷰)을 똑같이 씁니다. 다만 이번엔 **포트 경계·부수효과·경로 안전**을 스펙과 리뷰에 추가로 명시합니다.

> 💡 아래에서 스펙을 먼저 세우고, 계층별로 테스트-먼저로 내려갑니다.

---

## 1. 개념 빠르게 잡기

### 렌더링은 어댑터, 요약은 도메인, 저장 지휘는 유즈케이스

> - `summarize(conversation)` → **도메인**: 외부와 무관한 순수 규칙(턴 수·미리보기).
> - `render_markdown(conversation)` → **어댑터**: "어떤 형식으로 보여줄까"는 표현 관심사.
> - `TranscriptStorePort.save(session_id, conversation)` → **포트**가 도메인 객체를 받고, 어댑터가 렌더+저장. 그래서 **유즈케이스는 마크다운·파일을 모릅니다.**

### 왜 포트가 `conversation`을 통째로 받나

> 포트가 "완성된 문자열"이 아니라 **도메인 객체(Conversation)**를 받으면, 렌더링 방식(마크다운·JSON·HTML)을 어댑터마다 다르게 정할 수 있습니다. 유즈케이스는 "무엇을 저장할지(대화)"만 알고 "어떻게 보여줄지"는 어댑터에 맡깁니다.

---

## STEP 1 — 스펙 (배치까지 명시)

```markdown
## 기능: 세션 종료 시 대화 저장 + 요약

- 목적: 세션이 끝나면 대화를 파일로 남기고, 요약을 터미널에 출력.
- 도메인:
  - summarize(conversation) -> str : "N개 턴 · 시작: <첫 사용자 발화 미리보기>". 빈 대화는 "빈 대화".
- 포트(usecase/ports.py):
  - TranscriptStorePort.save(session_id: str, conversation: Conversation) -> None
- 유즈케이스(usecase/save_conversation.py):
  - SaveConversation(store).execute(conversation, session_id) -> str(요약)
  - 포트로 저장하고, summarize 결과를 돌려준다. 마크다운/파일을 몰라야 한다.
- 어댑터(adapter/transcript_store.py):
  - render_markdown(conversation) -> str : 턴을 마크다운으로.
  - FileTranscriptStore(directory).save(...) : 디렉터리 생성 → session_id 정규화(허용 문자만) → {id}.md 저장(UTF-8).
- 인프라(voice_handler.py):
  - 세션 중 어시스턴트 자막을 모아 Conversation에 턴으로 쌓기.
  - shutdown에서 SaveConversation 실행. 저장 실패는 예외를 밖으로 흘리지 말고 [저장 실패] 로그만.
- 규칙: 유즈케이스는 포트/도메인만 import. 도메인은 파일·마크다운 모름. 경로 주입 방지.
```

> 💡 스펙에 **계층별 배치와 시그니처**를 못박았습니다. 이게 AI가 계층을 흐트러뜨리지 않게 하는 가장 강력한 고삐입니다.

---

## STEP 2 — 🔴🟢 도메인 요약 + 포트 (테스트 먼저)

**① 테스트 먼저 프롬프트 (그대로 복붙)**

```text
규칙 파일과 위 스펙에 따라, 도메인 요약 summarize의 '실패하는' pytest 테스트를
tests/domain/test_summarize.py 에 먼저 작성해줘. 구현은 아직 만들지 마.
- 턴 2개(사용자+어시스턴트)일 때: 반환 문자열에 턴 수 "2"와 첫 사용자 발화 미리보기가 포함
- 빈 대화일 때: 정확히 "빈 대화" 반환
import는 voice_agent.domain.conversation / turn / summary 기준. 기존 스타일에 맞춰.
```

**🔴 테스트(사람 검토)** — `tests/domain/test_summarize.py`

```python
from voice_agent.domain.conversation import Conversation
from voice_agent.domain.summary import summarize
from voice_agent.domain.turn import Turn, Role


def test_summarize_counts_and_preview():
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="지금 몇 시야?"))
    convo.add_turn(Turn(role=Role.ASSISTANT, text="오후 3시예요."))

    out = summarize(convo)
    assert "2" in out                 # 턴 수
    assert "지금 몇 시" in out          # 첫 사용자 발화 미리보기


def test_summarize_empty():
    assert summarize(Conversation()) == "빈 대화"
```

**② 구현 프롬프트 (그대로 복붙)**

```text
방금 테스트를 통과하도록 구현해줘.
1) src/voice_agent/domain/summary.py 에 summarize(conversation) -> str
   - 빈 대화는 "빈 대화", 아니면 "{턴수}개 턴 · 시작: {첫 사용자 발화 30자 미리보기}"
   - 도메인이므로 외부 라이브러리·파일·Realtime 금지(순수 함수)
2) src/voice_agent/usecase/ports.py 에 TranscriptStorePort(Protocol) 추가
   - save(session_id: str, conversation: Conversation) -> None  (본문은 ...)
   - Conversation을 통째로 받는다(문자열 아님). 렌더링은 나중에 어댑터가 한다.
uv run pytest tests/domain/test_summarize.py 가 초록인지 확인해.
```

**🟢 구현(검토)** — `src/voice_agent/domain/summary.py`

```python
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
```

**포트 추가** — `src/voice_agent/usecase/ports.py` 에 아래를 추가

```python
from voice_agent.domain.conversation import Conversation   # 파일 위쪽 import에 추가


class TranscriptStorePort(Protocol):
    """대화를 어딘가에 저장하는 약속(파일·DB 등은 어댑터가 정한다)."""

    def save(self, session_id: str, conversation: Conversation) -> None:
        ...
```

```powershell
uv run pytest tests/domain/test_summarize.py
```

**예상 출력** (🟢): `2 passed`

> 💡 **도메인은 여전히 순수**합니다. `summary.py`는 파일·마크다운·Realtime을 모릅니다. 리뷰에서 이걸 확인합니다("도메인에 IO가 새어들지 않았는가").

---

## STEP 3 — 🔴🟢 어댑터: 렌더 + 파일 저장 (테스트 먼저)

**① 테스트 먼저 프롬프트 (그대로 복붙)**

```text
adapter/transcript_store.py 의 render_markdown과 FileTranscriptStore.save의
'실패하는' 테스트를 tests/adapter/test_transcript_store.py 에 먼저 써줘. 구현은 아직.
- render_markdown(conversation): 반환 마크다운에 각 턴 텍스트와 발화자 표시가 들어가는지
- save(tmp_path 사용): 지정 폴더에 {session_id}.md 파일이 생기고 내용이 들어갔는지
- 경로 주입 방어: session_id가 "../../evil" 이어도 상위 폴더에 파일이 안 생기고,
  지정 폴더 안에 정규화된 이름으로 저장되는지
pytest의 tmp_path 픽스처를 쓰고, 기존 import 스타일에 맞춰.
```

**🔴 테스트(검토)** — `tests/adapter/test_transcript_store.py`

```python
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
```

**② 구현 프롬프트 (그대로 복붙)**

```text
방금 테스트를 통과하도록 src/voice_agent/adapter/transcript_store.py 를 구현해줘.
1) render_markdown(conversation) -> str : 턴들을 마크다운으로(발화자 + 텍스트)
2) FileTranscriptStore(directory): TranscriptStorePort를 만족(save 시그니처 동일)
   - save에서 폴더 생성(mkdir parents/exist_ok)
   - 🛡️ session_id는 영숫자와 -_ 만 남겨 정규화(경로 주입 방지), 비면 "session"
   - 항상 지정 폴더 안의 {정규화된id}.md 로 UTF-8 저장, 내용은 render_markdown 결과
계층 규약: 이 파일은 adapter다. 도메인/인프라를 import하지 마(도메인 값객체는 사용 가능).
uv run pytest tests/adapter/test_transcript_store.py 초록 확인.
```

**🟢 구현(검토)** — `src/voice_agent/adapter/transcript_store.py`

```python
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
```

```powershell
uv run pytest tests/adapter/test_transcript_store.py
```

**예상 출력** (🟢): `3 passed`

> ⚠️ **경로 정규화가 핵심 리뷰 포인트**. `session_id`는 외부에서 올 수 있으니(신뢰 경계 밖), 파일 이름에 쓰기 전 허용 문자만 남깁니다. AI가 이 줄을 빠뜨리면 리뷰에서 반드시 잡습니다.

---

## STEP 4 — 🔴🟢 유즈케이스: `SaveConversation` (테스트 먼저)

**① 테스트 먼저 프롬프트 (그대로 복붙)**

```text
usecase/save_conversation.py 의 SaveConversation의 '실패하는' 테스트를
tests/usecase/test_save_conversation.py 에 먼저 써줘. 구현은 아직.
- FakeStore(무엇을 저장했는지 기록하는 가짜 저장소)를 만들고
- SaveConversation(store=FakeStore).execute(conversation, session_id="sess-9") 호출 시
  · store.save가 같은 session_id·conversation으로 호출됐는지
  · 반환값이 summarize 결과(요약 문자열)인지
유즈케이스는 포트/도메인만 쓰고 어댑터를 import하지 않는다는 전제로 작성.
```

**🔴 테스트(검토)** — `tests/usecase/test_save_conversation.py`

```python
from voice_agent.domain.conversation import Conversation
from voice_agent.domain.turn import Turn, Role
from voice_agent.usecase.save_conversation import SaveConversation


class FakeStore:
    """테스트용 가짜 저장소. 무엇을 저장했는지 기록한다."""
    def __init__(self):
        self.saved = None

    def save(self, session_id, conversation):
        self.saved = (session_id, conversation)


def test_saves_and_returns_summary():
    store = FakeStore()
    convo = Conversation()
    convo.add_turn(Turn(role=Role.USER, text="안녕"))

    usecase = SaveConversation(store=store)
    summary = usecase.execute(convo, session_id="sess-9")

    # 저장이 실제로 호출됐고(같은 대화·id)
    assert store.saved[0] == "sess-9"
    assert store.saved[1] is convo
    # 반환값이 요약이다
    assert "1" in summary
```

**② 구현 프롬프트 (그대로 복붙)**

```text
방금 테스트를 통과하도록 src/voice_agent/usecase/save_conversation.py 를 구현해줘.
- SaveConversation(store: TranscriptStorePort)
- execute(conversation, session_id) -> str:
    store.save(session_id, conversation) 로 저장하고, domain의 summarize(conversation) 반환
중요(계층 규약): 이 파일은 usecase다. adapter를 import하지 마라(포트·도메인만).
마크다운·파일 얘기는 여기 없어야 한다(어댑터가 담당).
uv run pytest tests/usecase/test_save_conversation.py 초록 확인.
```

**🟢 구현(검토)** — `src/voice_agent/usecase/save_conversation.py`

```python
from voice_agent.domain.conversation import Conversation
from voice_agent.domain.summary import summarize
from voice_agent.usecase.ports import TranscriptStorePort


class SaveConversation:
    """대화를 저장하고 요약을 돌려준다. 마크다운·파일은 모른다(포트에 위임)."""

    def __init__(self, store: TranscriptStorePort):
        self._store = store

    def execute(self, conversation: Conversation, session_id: str) -> str:
        self._store.save(session_id, conversation)   # 어떻게 저장할지는 어댑터 몫
        return summarize(conversation)               # 도메인 요약을 돌려준다
```

```powershell
uv run pytest tests/usecase/test_save_conversation.py
```

**예상 출력** (🟢): `1 passed`

> 💡 **유즈케이스 import를 리뷰**: `save_conversation.py`는 `adapter`를 **import하지 않습니다**(포트·도메인만). 이 한 줄 확인이 계층 붕괴를 막습니다.

---

## STEP 5 — 핸들러 결선 (실행·관찰)

세션 중 어시스턴트 자막을 모아 대화를 만들고, 종료 시 저장합니다. 핸들러는 실행·관찰 영역이라, 결선을 **한 프롬프트로 요청**하고 리뷰로 검증합니다.

**결선 프롬프트 (그대로 복붙)**

```text
infra의 voice_handler.py에 대화 저장을 결선해줘.
1) __init__: uuid로 8자리 self._session_id 생성, 빈 self._conversation(Conversation),
   self._assistant_buffer="" 준비, self._save = SaveConversation(FileTranscriptStore("transcripts"))
2) _read_events: 어시스턴트 자막 delta를 self._assistant_buffer에 이어붙이고,
   response.done을 만나면 버퍼가 비어있지 않을 때 Role.ASSISTANT 턴으로 self._conversation에 추가한 뒤 버퍼 비우기
3) shutdown: 세션 close 후 self._save.execute(self._conversation, self._session_id) 실행,
   결과 요약을 [저장됨] 로그로 출력. 단, 저장 실패가 종료를 막지 않게 try/except OSError로 감싸 [저장 실패] 로그만.
기존 자막 출력·음성 재생·바지인 로직은 건드리지 마. 계층 규약 유지.
```

아래는 이 프롬프트로 나온 결과의 **검토용 예시**입니다. **바뀌는 곳만** 표시합니다.

`__init__`에 대화 버퍼와 저장 유즈케이스를 준비합니다.

```python
        import uuid
        from voice_agent.domain.conversation import Conversation
        from voice_agent.usecase.save_conversation import SaveConversation
        from voice_agent.adapter.transcript_store import FileTranscriptStore

        self._conversation = Conversation()               # 이번 세션의 대화
        self._assistant_buffer = ""                       # 진행 중 어시스턴트 자막 조각들
        self._session_id = uuid.uuid4().hex[:8]           # 세션 식별자
        self._save = SaveConversation(store=FileTranscriptStore(directory="transcripts"))
```

`_read_events`에서 자막 조각을 모으고, 응답이 끝나면 한 턴으로 확정합니다(자막 출력 분기 옆).

```python
                text = extract_transcript_delta(event)
                if text:
                    print(text, end="", flush=True)
                    self._assistant_buffer += text        # 조각을 모은다
                    continue
                ...
                elif event.get("type") == "response.done":
                    # 한 응답이 끝나면 모은 자막을 어시스턴트 턴으로 확정.
                    if self._assistant_buffer.strip():
                        from voice_agent.domain.turn import Turn, Role
                        self._conversation.add_turn(
                            Turn(role=Role.ASSISTANT, text=self._assistant_buffer.strip())
                        )
                    self._assistant_buffer = ""
                    print(flush=True)
```

`shutdown`에서 저장합니다. **저장 실패가 종료를 막지 않게** 감쌉니다.

```python
    async def shutdown(self) -> None:
        if self._session is not None:
            await self._session.close()
        # 부수효과는 조용히: 저장 실패해도 세션 종료는 정상 진행.
        try:
            summary = self._save.execute(self._conversation, self._session_id)
            print(f"\n[저장됨] transcripts/{self._session_id}.md · {summary}", flush=True)
        except OSError as exc:
            print(f"\n[저장 실패] {exc}", flush=True)
```

> 💡 **부수효과 격리**: 파일 저장이 실패해도(디스크·권한) `try/except OSError`로 감싸 세션은 깔끔히 끝납니다. "실패해도 안전하게"는 5·6교시의 종료 처리 감각과 같습니다.

---

## STEP 6 — 리뷰 체크리스트 (큰 기능용 확장) + 실행

큰 기능이라 리뷰 항목도 늡니다. **사람이 모두 확인**한 뒤 병합합니다.

- [ ] **포트 경계**: 유즈케이스가 `adapter`를 import하지 않는가?(포트·도메인만)
- [ ] **도메인 순수성**: `summary.py`에 파일·마크다운·Realtime이 없는가?
- [ ] **표현 분리**: 마크다운 렌더는 어댑터에만 있는가?
- [ ] **경로 안전**: `session_id` 정규화로 지정 폴더 밖에 못 쓰는가?
- [ ] **부수효과 안전**: 저장 실패가 세션 종료를 막지 않는가?(`try/except`)
- [ ] **전체 초록**: `uv run pytest` 전체 통과(기존 안 깨짐)
- [ ] **ruff 통과** / 군더더기 없음

**실행 관찰**:

```powershell
uv run uvicorn voice_app:app --host 127.0.0.1 --port 7860
```

몇 마디 대화한 뒤 브라우저에서 **중지**를 누르면, 터미널에 저장 로그가 뜨고 `transcripts/` 폴더에 `.md`가 생깁니다.

**예상 출력** (터미널, 예시):

```text
[종료] 세션이 닫혔습니다
[저장됨] transcripts/a1b2c3d4.md · 4개 턴 · 시작: 지금 몇 시야?
```

> ⚠️ **관찰형 확인**: 완성 신호는 **"세션을 끝내면 `transcripts/`에 대화 마크다운이 생기고, 요약이 출력된다"**, 그리고 **저장이 실패해도 세션은 정상 종료된다**입니다. (요약·렌더·저장·유즈케이스 로직은 STEP 2~4에서 이미 TDD로 검증했습니다.)

---

## 🧪 이 교시 체크리스트

- [x] `test_summarize_counts_and_preview` / `test_summarize_empty`
- [x] `test_render_markdown_contains_turns`
- [x] `test_saves_file` / `test_sanitizes_session_id`
- [x] `test_saves_and_returns_summary`

**🎯 필수 미션 (다음 교시 진행 전 반드시 완성)**
- [ ] 미션 1 — 사용자 발화 전사도 대화에 포함(입력 전사 켜기, 5교시 선택미션 연계)
- [ ] 미션 2 — 저장 실패 상황을 가짜 저장소로 재현해, 세션이 예외 없이 끝나는지 테스트

**🟦 선택 (여유 있으면)**
- [ ] 미션 3 — 요약을 모델에게 맡기기(짧은 요약 프롬프트로 `response.create`) — 실제 LLM 요약

> 💡 막히면 맨 아래 **🧩 필수 미션 — 풀이** 를 펼쳐 보세요.

---

## ✅ 완성 체크포인트 (= 바이브 코딩 ② 게이트)

- [ ] `domain/summary.py`, `usecase/ports.py`(포트), `usecase/save_conversation.py`, `adapter/transcript_store.py` 존재
- [ ] 유즈케이스가 포트·도메인만 의존(어댑터 import 없음)
- [ ] `session_id` 경로 정규화 + 저장 실패 `try/except`
- [ ] `uv run pytest` → 이전 개수 + 이 교시 테스트만큼 증가, 전체 초록
- [ ] `uv run ruff check src/voice_agent` → **All checks passed!**
- [ ] STEP 6 리뷰 체크리스트를 **사람이 모두 확인**
- [ ] **실행 관찰**: 세션 종료 시 `transcripts/*.md` 생성 + 요약 출력

> **계층 규칙 자가 점검**: 저장이라는 부수효과가 들어와도 경계는 유지됩니다 — 도메인(요약)·유즈케이스(지휘)·포트(약속)·어댑터(파일·마크다운)·인프라(결선)가 각자 자리를 지킵니다.

---

## ⚠️ 자주 나는 오류 & 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| 유즈케이스가 마크다운을 앎 | 렌더링을 유즈케이스에 둠 | 렌더는 어댑터로, 포트는 Conversation을 받게 |
| 도메인에 `pathlib` 등장 | 저장 로직이 도메인에 샘 | 파일 IO는 어댑터로 이동 |
| 상위 폴더에 파일 생성됨 | `session_id` 정규화 누락 | 허용 문자만 남기는 정규화 확인 |
| 저장 실패로 앱이 죽음 | 예외 미포착 | `shutdown`에서 `try/except OSError` |
| 대화가 비어 저장됨 | 자막 버퍼를 턴으로 확정 안 함 | `response.done`에서 버퍼→턴 추가 확인 |
| `Unknown parameter: 'session.input_audio_transcription'` | 전사 설정을 세션 최상위에 넣음(구 베타 키) | GA는 `session.audio.input.transcription: {"model": ...}` 위치로 |
| 사용자 턴이 안 쌓임(어시스턴트만 저장) | 전사 미활성 또는 이벤트 타입 불일치 | 위 전사 설정 확인 + `conversation.item.input_audio_transcription.completed` 처리 확인 |
| 기존 테스트 깨짐 | 공유 코드 변경 | 전체 pytest로 확인, 규약(초록 유지) 준수 |

---

## 📖 용어 사전 (이 교시 신규)

- **부수효과(side effect)**: 값 반환 외에 바깥 상태를 바꾸는 동작(파일 쓰기·네트워크 등).
- **포트(port) 재확인**: 바깥과 닿는 기능(저장 등)을 약속으로 감싸 유즈케이스와 분리.
- **표현 분리(presentation)**: "어떻게 보여줄지"(마크다운 등)는 어댑터의 관심사.
- **경로 주입(path injection)**: 파일 이름/경로에 위험 값을 넣어 의도 밖 위치에 접근하는 공격.
- **정규화(sanitize)**: 위험 문자를 제거해 안전한 값만 남기는 것.
- **`tmp_path`**: pytest가 주는 임시 폴더 픽스처(파일 테스트에 사용, 자동 정리).

---

## 🎯 필수 미션 — 다음 교시로 가기 전 반드시 완성

직접 해보고, **막히면 접이식 풀이**를 펼치세요.

### 미션 1 (필수) — 사용자 발화도 기록

세션 설정의 **`audio.input.transcription`**(GA 위치)에 입력 전사를 켜고, 사용자 발화 전사 완료 이벤트를 잡아 `Role.USER` 턴으로 대화에 추가하세요.
- **어디에**: 세션 `open`(어댑터) + `_read_events`(인프라)
- **왜**: 저장된 대화가 양쪽 발화를 모두 담아야 유용

### 미션 2 (필수) — 저장 실패 안전성 테스트

`save`가 `OSError`를 던지는 가짜 저장소로 `SaveConversation.execute`(또는 shutdown 경로)가 예외를 밖으로 흘리지 않는지 확인하세요.
- **어디에**: `tests/usecase/test_save_conversation.py` 또는 핸들러 테스트

> 풀이는 아래 **🧩 필수 미션 — 풀이** 에 접이식으로 있습니다.

### 🟦 선택 (여유 있으면) — 모델 요약

저장 직전, 짧은 요약을 모델에게 요청해 사람이 읽기 좋은 한 문장 요약을 만들어 보세요. 계층을 지키는 설계(포트로 감싸기)와 복붙 프롬프트는 아래 **풀이 3**에 있습니다.

---

## 🧩 필수 미션 — 풀이 (막히면 펼치기)

<details>
<summary><strong>📂 풀이 1 — 사용자 발화도 기록</strong> &nbsp;<sub>(클릭하여 펼치기)</sub></summary>

**① AI에게 줄 프롬프트 (그대로 복붙)**

```text
사용자 발화도 대화 기록에 포함되게 해줘. GA(gpt-realtime) 세션 구조를 정확히 지켜라.
1) 어댑터 세션 open()의 session.update에서, session.audio.input 안에
   "transcription": {"model": "gpt-4o-mini-transcribe"} 를 추가한다.
   ⚠️ 절대 session 최상위에 "input_audio_transcription"를 넣지 마라(구 베타 키).
      GA에서는 session.audio.input.transcription 이 올바른 위치다.
2) 인프라 핸들러 _read_events에서 사용자 입력 전사 완료 이벤트
   "conversation.item.input_audio_transcription.completed"를 받으면
   event["transcript"]를 Role.USER 턴으로 self._conversation에 추가한다.
계층 규약을 지키고(도메인은 순수), 기존 테스트는 깨지 마.
```

**② 반영 예시(사람 검토용)** — 세션 설정: `open`의 **`audio.input` 블록 안**에 `transcription` 한 줄을 추가합니다(5교시에서 만든 `format`·`turn_detection` 옆).

```python
            "audio": {
                "input": {
                    "format": {"type": "audio/pcm", "rate": 24000},
                    "turn_detection": {"type": "semantic_vad"},
                    "transcription": {"model": "gpt-4o-mini-transcribe"},  # ← 이 줄 추가
                },
                "output": { ... },   # 기존 그대로
            },
```

> ⚠️ **핵심**: GA에서 입력 전사는 `session.audio.input.transcription` 아래에 `{"model": ...}` 형태로 들어갑니다. 구 베타의 `session.input_audio_transcription`(세션 최상위)로 넣으면 서버가 **`Unknown parameter: 'session.input_audio_transcription'`** 오류를 냅니다. 모델은 `gpt-4o-mini-transcribe`(권장) 또는 `whisper-1`을 씁니다.

**핸들러**(`_read_events`)에서 사용자 전사 완료 이벤트를 턴으로:

```python
                if event.get("type") == "conversation.item.input_audio_transcription.completed":
                    from voice_agent.domain.turn import Turn, Role
                    said = event.get("transcript", "").strip()
                    if said:
                        self._conversation.add_turn(Turn(role=Role.USER, text=said))
                    continue
```

> 💡 전사가 조각으로 오는 `...input_audio_transcription.delta`(부분)와 `...completed`(최종)가 있습니다. 대화 기록엔 **`.completed`의 `transcript`(최종본)**만 턴으로 넣으면 깔끔합니다. 이벤트 이름이 의심되면 임시 `print(event.get("type"))`로 실제 타입을 확인하세요(5교시 진단법).

</details>

---

<details>
<summary><strong>📂 풀이 2 — 저장 실패 안전성</strong> &nbsp;<sub>(클릭하여 펼치기)</sub></summary>

**① AI에게 줄 프롬프트 (그대로 복붙)**

```text
저장 실패 안전성을 테스트로 고정해줘.
tests/usecase/test_save_conversation.py 에:
- save()가 OSError를 던지는 BrokenStore(가짜 저장소)를 만들고
- SaveConversation.execute가 그 예외를 '숨기지 않고 그대로 던지는지'
  pytest.raises(OSError)로 검증하는 테스트를 추가해.
유즈케이스는 예외를 삼키지 않는 게 맞다(방어는 인프라 shutdown의 try/except에서 함).
기존 테스트는 깨지 마.
```

**② AI가 만든 테스트(사람 검토용)** — `tests/usecase/test_save_conversation.py` 에 추가

```python
import pytest

from voice_agent.domain.conversation import Conversation
from voice_agent.usecase.save_conversation import SaveConversation


class BrokenStore:
    def save(self, session_id, conversation):
        raise OSError("disk full")


def test_execute_propagates_but_handler_guards():
    # 유즈케이스 자체는 예외를 던진다(정직하게).
    usecase = SaveConversation(store=BrokenStore())
    with pytest.raises(OSError):
        usecase.execute(Conversation(), "sess")
```

**③ 핵심**: 유즈케이스는 예외를 **숨기지 않습니다**(정직). 대신 **핸들러 `shutdown`이 `try/except`로 감싸** 세션 종료를 지킵니다(STEP 5). 즉, "안전 처리"는 부수효과가 일어나는 경계(인프라)에서 합니다.

```powershell
uv run pytest tests/usecase/test_save_conversation.py
```

> 💡 **어디서 방어하나**: 순수 로직(유즈케이스)은 실패를 정직하게 알리고, 실제 IO 경계(핸들러)에서 감쌉니다. 방어를 한 겹에 몰지 않고 **적절한 층**에 둡니다. 프롬프트에도 이 방침을 명시해, AI가 유즈케이스에서 예외를 삼키지 않게 했습니다.

</details>

---

<details>
<summary><strong>📂 풀이 3 (선택) — 모델에게 한 문장 요약 맡기기</strong> &nbsp;<sub>(클릭하여 펼치기)</sub></summary>

지금 `summarize`는 "N개 턴 · 시작: …"처럼 기계적입니다. 사람이 읽기 좋은 한 문장 요약은 **모델**에게 맡기는 게 낫습니다. 다만 계층을 지켜야 하니, "요약을 만드는 능력"도 **포트**로 감쌉니다.

**① 설계 판단(먼저 정하기)**

- 모델 호출은 외부와 닿는 일 → **포트**로 감싼다: `SummarizerPort.summarize(conversation) -> str`.
- 실제 구현(어댑터)은 Realtime/모델로 한 문장 요약을 받는다.
- 유즈케이스는 포트만 알고, 모델·프롬프트는 모른다(도메인 `summarize`는 폴백으로 유지).

**② AI에게 줄 프롬프트 (그대로 복붙)**

```text
대화 저장 시 '사람이 읽기 좋은 한 문장 요약'을 모델로 만들고 싶어. 계층을 지켜서 구현해줘.

1) usecase/ports.py 에 SummarizerPort(Protocol) 추가:
   summarize(conversation: Conversation) -> str
2) adapter/model_summarizer.py 에 ModelSummarizer 구현:
   - 대화를 짧은 텍스트로 정리해 모델에게 "한 문장으로 요약해줘"라고 요청하고
     응답 텍스트를 돌려준다(실제 모델 호출부는 기존 세션/연결 방식을 따른다).
   - 실패하면(네트워크 등) 예외를 던진다. 절대 조용히 빈 문자열을 반환하지 마.
3) usecase/save_conversation.py 를 확장:
   - 생성자에 summarizer: SummarizerPort | None = None (선택 주입)
   - execute에서 summarizer가 있으면 그걸로 요약, 없거나 실패하면
     도메인 summarize(conversation)로 폴백.
4) 이 폴백 동작을 검증하는 테스트를 tests/usecase/ 에 추가:
   - FakeSummarizer(정상): 그 문장이 반환되는지
   - BrokenSummarizer(예외): 도메인 summarize 결과로 폴백되는지

규칙: 유즈케이스는 포트/도메인만 import(어댑터 import 금지). 도메인은 모델을 모름.
기존 테스트는 모두 초록 유지.
```

**③ 검토 포인트(사람이 승인)**

- 유즈케이스가 `adapter/model_summarizer`를 **import하지 않는가?**(포트만)
- 모델 요약 **실패 시 도메인 요약으로 폴백**해, 저장 자체는 항상 되는가?
- `summarizer=None`이면 13교시 본문과 **똑같이** 동작하는가?(하위 호환)
- 폴백 경로가 테스트로 **고정**됐는가?

**④ 실행**

```powershell
uv run pytest tests/usecase
```

> 💡 **왜 폴백인가**: 모델 요약은 실패할 수 있는 부수효과입니다. 실패해도 **저장과 기본 요약은 반드시 되도록** 도메인 요약을 안전망으로 둡니다. "좋은 것(모델 요약)은 시도하되, 없어도 망가지지 않게"가 핵심입니다.

</details>

---

### ✅ 미션 완료 확인 (= 진행 게이트)

```powershell
uv run pytest
uv run ruff check src/voice_agent
```

- 전체 초록(기존 + 저장 기능), ruff 통과.
- STEP 6 리뷰 체크리스트를 **모두 사람이 확인**.
- 세션 종료 시 `transcripts/*.md` 생성 + 요약 출력.

이 세 가지가 되면 게이트 통과입니다.

---

**다음 교시 예고 — 14교시(정리)**: 전체를 되짚습니다. 완성한 보이스 에이전트의 구조(계층·도구·가드레일·저장)를 한눈에 정리하고, 배포·확장·다음 단계를 안내합니다. 손으로 쌓은 토대와 바이브 코딩 가속을 잇는 마무리입니다.
> **선행**: 위 바이브 코딩 ② 게이트(전체 초록 + 리뷰 완료 + 저장 관찰) 통과 상태.
