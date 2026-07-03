# 12교시 — 바이브 코딩 ①: 토대 위에서 AI와 페어 코딩

> **이 교시가 끝나면** 1~11교시에서 손으로 쌓은 토대(계층·테스트·가드레일) 위에, **AI 코딩 에이전트와 함께** 새 기능을 빠르고 안전하게 추가합니다. 핵심은 속도가 아니라 **통제**입니다 — AI에게 규칙·스펙·테스트를 먼저 주고, 결과를 리뷰로 검증합니다.

---

## 0. 이 교시에 만드는 것 (한눈에)

지금까지는 한 줄씩 직접 쌓았습니다. 이제 그 위에서 **바이브 코딩**으로 새 도구 하나를 몇 분 만에 추가합니다. 단, "AI가 짜준 걸 그냥 붙이기"가 아니라, 우리가 만든 **안전망(테스트·가드레일·계층 경계)**을 그대로 활용해 검증합니다.

```
사람: 규칙(계층·TDD·가드레일 규약)을 AI에게 알려줌   ← STEP 1
사람: 스펙 한 문단 작성                              ← STEP 2
AI:   실패하는 테스트(RED) 먼저 생성 → 사람이 검토     ← STEP 3
AI:   테스트를 통과시키는 구현(GREEN) → 파이프라인 준수 ← STEP 4
사람: 리뷰 체크리스트로 검증 + 토글 등록              ← STEP 5
```

이 교시의 실습 기능: **길이 단위 변환 `convert_length`**(m·km·cm·mi). 5·10·11교시의 도구 패턴을 그대로 따르므로, "AI가 우리 규약을 지키는지"를 확인하기에 좋습니다.

> ⚠️ **왜 이제야 바이브 코딩인가**: 계층이 잘 나뉘고, 테스트가 촘촘하고, 가드레일이 한 파이프라인에 모여 있어야 **AI에게 맡겨도 안전**합니다. 토대가 부실하면 AI는 그 부실함을 빠르게 복제합니다. 1~11교시가 그 토대였습니다.

---

## 🧭 잠깐, 배경지식

이 교시의 핵심인 **바이브 코딩(vibe coding)**과 통제 방법을 짚습니다.

**① 바이브 코딩(vibe coding) / AI 페어 코딩.** 자연어로 의도를 말하면 AI 코딩 에이전트가 코드를 만들어 주는 방식입니다. 짝 프로그래밍의 파트너가 사람이 아니라 AI인 셈입니다. 빠르지만, **방향을 잡는 건 여전히 사람**입니다.

**② AI는 신뢰 경계 밖(9교시와 같은 원칙).** 모델이 준 함수 인자를 검증했듯, AI가 준 **코드도 검증**합니다. 대체로 훌륭하지만, 미묘하게 규약을 어기거나(계층 침범), 엣지 케이스를 놓치거나, 없는 API를 지어낼 수 있습니다. 그래서 **테스트와 리뷰**가 안전망입니다.

**③ 통제의 세 축.** AI를 잘 쓰는 비결은 세 가지를 **먼저** 주는 것입니다. (1) **컨텍스트** — 이 코드베이스의 규칙(계층·명명·가드레일). (2) **스펙** — 무엇을 만들지 한 문단으로. (3) **테스트** — 무엇이 맞는지 실행 가능한 기준. 이 셋이 있으면 AI 출력이 **검증 가능**해집니다.

**④ 테스트 먼저(Test-First)가 AI의 고삐.** 구현부터 시키면 "그럴듯하지만 틀린" 코드를 받기 쉽습니다. **실패하는 테스트를 먼저** 만들어(RED) 사람이 검토하고, 그다음 "이 테스트를 통과시켜"(GREEN)라고 하면, AI의 자유도를 좁혀 **원하는 것만** 만들게 됩니다.

**⑤ 리뷰는 생략 불가.** 바이브 코딩에서 가장 흔한 실수는 "돌아가니까 통과"입니다. 테스트 통과는 필요조건일 뿐입니다. 계층 경계·가드레일·명명·불필요한 의존성을 **사람이 눈으로** 확인해야 합니다.

> 💡 아래에서 이 다섯 가지를 실제 흐름으로 실습합니다.

---

## 1. 개념 빠르게 잡기

### 도구는 무엇이든 좋다 (Copilot Agent Mode · Claude Code 등)

> 이 교시의 방법은 특정 AI 도구에 매이지 않습니다. **편집기 안에서 파일을 읽고/쓰고/테스트를 돌리는** 에이전트형 AI라면 무엇이든 됩니다(예: GitHub Copilot Agent Mode, Claude Code). 공통 원리는 "규칙 파일 → 스펙 → 테스트 먼저 → 구현 → 리뷰"입니다.

### 규칙 파일이 왜 결정적인가

> AI는 **이 대화(또는 프로젝트)에서 준 규칙**을 우선 따릅니다. "계층을 침범하지 마라", "실행 전 가드레일을 거쳐라", "테스트부터 써라" 같은 규약을 파일로 고정해 두면, 매번 설명하지 않아도 AI가 그 틀 안에서 작업합니다. 스펙 주도 개발(SDD)의 헌장(constitution)과 같은 역할입니다.

---

## STEP 1 — AI에게 줄 프로젝트 규칙 파일

프로젝트 루트에 규칙 파일을 둡니다. 도구에 따라 이름이 다릅니다(예: `.github/copilot-instructions.md`, 또는 루트의 `AGENTS.md`/`CLAUDE.md`). 내용은 같습니다 — **이 코드베이스에서 지켜야 할 규약**.

```markdown
# 프로젝트 규약 (AI 코딩 에이전트용)

## 아키텍처 (Clean Architecture)
- 계층: domain → usecase → adapter → infra. 안쪽은 바깥을 import하지 않는다.
- 도메인은 순수 파이썬만(외부 라이브러리·네트워크·Realtime 금지).
- 통신/JSON/base64는 adapter, 큐·핸들러·IO는 infra.

## 테스트 (Test-First TDD)
- 새 기능은 반드시 실패하는 테스트(RED)부터 쓴다. 그다음 최소 구현(GREEN).
- pytest 사용(uv run pytest). async 테스트는 `async def`.
- 기존 테스트를 깨지 않는다(리팩터는 초록 유지).

## 도구 추가 규약 (8~11교시 패턴)
- 순수 함수는 adapter에, 명세(ToolSpec)는 TOOL_SPECS에 등록.
- 실행은 반드시 dispatch_tool 파이프라인을 지난다(빈도→존재→인자→실행).
- 외부/모델 입력은 신뢰하지 않는다: 정규화 후 허용 목록·범위 검증, 실패는 ValueError.
- 결과는 JSON 문자열(ensure_ascii=False).

## 스타일
- ruff 통과. 한글 주석 허용. 함수는 작게, 이름은 의도를 드러내게.
```

> 💡 **이 파일이 곧 고삐입니다.** AI는 이 규약을 근거로 "도메인에 requests를 넣지 않기", "dispatch_tool을 거치기" 같은 판단을 합니다. 규약이 명확할수록 AI 출력이 우리 코드베이스에 자연스럽게 맞습니다.

---

## STEP 2 — 스펙 한 문단 쓰기

만들 기능을 **짧고 분명하게** 적습니다. 스펙이 모호하면 AI 출력도 모호해집니다.

```markdown
## 기능: 길이 단위 변환 도구 convert_length

- 목적: "3km는 몇 미터야?" 같은 길이 변환 질문에 답한다.
- 지원 단위(허용 목록): m, km, cm, mi(마일).
- 입력: value(number), from_unit(string), to_unit(string).
- 규칙: 단위는 정규화(공백·대소문자) 후 허용 목록 검사. 밖이면 ValueError.
- 음수 길이는 ValueError(길이는 0 이상).
- 결과: "3 km = 3000.0 m" 형태의 문자열.
- 등록: TOOL_SPECS/TOOL_HANDLERS에 추가, 핸들러 토글에 포함.
- 배치: 변환 로직은 adapter/length.py, 도구 래퍼는 adapter/tools.py.
```

> 💡 스펙에 **허용 목록·검증·배치·등록**까지 적었습니다. 이렇게 규칙을 스펙에 녹이면, AI가 가드레일과 계층을 빠뜨릴 여지가 줄어듭니다.

---

## STEP 3 — 🔴 테스트 먼저 (AI에게 RED 요청 → 사람 검토)

구현보다 **테스트를 먼저** 만들게 합니다.

**테스트 먼저 프롬프트 (그대로 복붙)**

```text
위 규약과 스펙에 따라 convert_length의 '실패하는' pytest 테스트를
tests/adapter/test_length.py 에 작성해줘. 구현은 아직 만들지 마.
포함할 케이스:
- 지원 단위 집합이 {m, km, cm, mi} 인지
- km↔m 기본 변환(예: 3km = 3000m)
- 같은 단위는 그대로(예: 5m→5m)
- 지원 밖 단위 거부(ValueError)
- 음수 길이 거부(ValueError)
기존 테스트 스타일·import에 맞추고, 함수 이름은 test_로 시작.
```

AI가 만든 테스트를 **사람이 검토**합니다. 아래처럼 나오는 게 이상적입니다.

```python
import pytest

from voice_agent.adapter.length import convert_length, SUPPORTED


def test_supported_units():
    assert SUPPORTED == {"m", "km", "cm", "mi"}


def test_km_to_m():
    assert convert_length(value=3, from_unit="km", to_unit="m") == 3000


def test_same_unit_identity():
    assert convert_length(value=5, from_unit="m", to_unit="m") == 5


def test_rejects_unsupported_unit():
    with pytest.raises(ValueError):
        convert_length(value=1, from_unit="m", to_unit="light-year")


def test_rejects_negative_length():
    with pytest.raises(ValueError):
        convert_length(value=-1, from_unit="m", to_unit="cm")
```

**검토 포인트**(사람이 확인):
- 스펙의 규칙(허용 목록·음수 거부)이 **테스트로 표현**됐는가?
- 단위 이름·기대값이 맞는가? (예: 1mi ≈ 1609.34m)
- 빠진 엣지 케이스는 없는가?

```powershell
uv run pytest tests/adapter/test_length.py
```

**예상 출력** (🔴): `ModuleNotFoundError: ...length` — 아직 구현이 없으니 정상.

> ⚠️ **테스트를 사람이 검토하는 이유**: 테스트가 곧 "정답 기준"입니다. 기준이 틀리면 그 위의 구현도 틀립니다. AI가 만든 테스트라도 **사람이 기준을 승인**해야 합니다.

---

## STEP 4 — 🟢 구현 (AI에게 GREEN 요청 → 규약 준수 확인)

이제 테스트를 통과시키는 구현을 요청합니다.

**구현 프롬프트 (그대로 복붙)**

```text
방금 테스트를 통과하도록 구현해줘.
1) src/voice_agent/adapter/length.py 에 convert_length(value, from_unit, to_unit)와 SUPPORTED
   - 단위 정규화(공백·대소문자) → 허용 목록 검사(밖이면 ValueError)
   - 음수 길이는 ValueError
   - '미터 허브' 방식으로 변환(from → 미터 → to)
2) adapter/tools.py 에 convert_length_tool 래퍼 추가 + TOOL_SPECS·TOOL_HANDLERS 등록
3) 핸들러 __init__ 토글에 convert_length 추가
규약 준수: 실행은 기존 dispatch_tool 파이프라인을 그대로 지나야 한다(핸들러는 dispatch_tool 한 줄 유지).
계층: 변환 구현은 adapter다(도메인 아님). uv run pytest 전체가 초록인지 확인해.
```

AI가 만든 구현 예시(사람이 검토):

```python
# src/voice_agent/adapter/length.py
_TO_METER = {"m": 1.0, "km": 1000.0, "cm": 0.01, "mi": 1609.34}   # 1 단위 = ? 미터
SUPPORTED = set(_TO_METER)


def convert_length(value: float, from_unit: str, to_unit: str) -> float:
    src = from_unit.strip().lower()          # 정규화
    dst = to_unit.strip().lower()
    for unit in (src, dst):                   # 허용 목록 검사
        if unit not in SUPPORTED:
            raise ValueError(f"지원하지 않는 단위: {unit}")
    if value < 0:                             # 정책: 음수 길이 금지
        raise ValueError("길이는 0 이상이어야 합니다.")
    meters = value * _TO_METER[src]           # from → 미터(허브)
    return round(meters / _TO_METER[dst], 2)  # 미터 → to
```

```powershell
uv run pytest tests/adapter/test_length.py
```

**예상 출력** (🟢): `5 passed`

> 💡 **미터 허브 기법**이 또 보입니다(11교시 섭씨 허브와 같은 꼴). AI가 우리 코드베이스의 관용구를 따라오는지 확인하는 포인트입니다. 안 따라오면, 규칙 파일에 그 관용구를 명시해 다시 요청합니다.

---

## STEP 5 — 리뷰 체크리스트 (사람이 최종 승인)

테스트가 초록이어도, **아래를 사람이 확인**하기 전에는 병합하지 않습니다.

- [ ] **계층 경계**: `length.py`(adapter)가 도메인·인프라를 침범하지 않는가? 도메인에 외부 의존이 들어가지 않았는가?
- [ ] **가드레일 통과**: 새 도구가 `dispatch_tool` 파이프라인을 지나는가? (핸들러가 여전히 `dispatch_tool` 한 줄인가)
- [ ] **입력 검증**: 정규화 → 허용 목록 → 범위(음수) 순으로 막는가?
- [ ] **등록 일관성**: `TOOL_SPECS`·`TOOL_HANDLERS`·토글에 모두 추가됐는가?
- [ ] **전체 초록 유지**: `uv run pytest` 전체가 통과하는가? (기존 테스트 안 깨짐)
- [ ] **ruff 통과**: `uv run ruff check src/voice_agent`
- [ ] **군더더기 없음**: 안 쓰는 import·죽은 코드·과한 추상화가 없는가?

전부 만족하면 승인합니다. 하나라도 걸리면 **그 항목을 콕 집어** AI에게 수정 요청합니다("도메인 규칙이 아니라 adapter에 두자", "dispatch_tool을 거치게 해줘").

**실행 관찰**:

```powershell
uv run uvicorn voice_app:app --host 127.0.0.1 --port 7860
```

- **"3km는 몇 미터야?"** → `[도구] convert_length(...)` → "3000미터예요."

> ⚠️ **관찰형 확인**: 완성 신호는 **"길이 질문이 새 도구로 처리되고, 기존 다섯 도구와 같은 가드레일을 지난다"**입니다. 그리고 **전체 테스트가 여전히 초록**입니다.

---

## 🧪 이 교시 체크리스트

이 교시는 **AI가 테스트도 함께 생성**하므로, 개수보다 **품질과 규약 준수**로 확인합니다.

- [x] `test_supported_units` / `test_km_to_m` / `test_same_unit_identity`
- [x] `test_rejects_unsupported_unit` / `test_rejects_negative_length`

**🎯 필수 미션 (다음 교시 진행 전 반드시 완성)**
- [ ] 미션 1 — cm·mi 왕복 정확도 테스트를 AI로 추가하고 사람이 검토
- [ ] 미션 2 — 리뷰에서 일부러 한 가지를 어긴 코드를 받게 하고(예: 도메인 침범), 리뷰로 잡아 수정 요청

**🟦 선택 (여유 있으면)**
- [ ] 미션 3 — 규칙 파일에 "함수 20줄 이하" 같은 규약을 추가하고, AI가 지키는지 확인

> 💡 막히면 맨 아래 **🧩 필수 미션 — 풀이** 를 펼쳐 보세요.

---

## ✅ 완성 체크포인트 (= 바이브 코딩 ① 게이트)

- [ ] 프로젝트 규칙 파일 존재(아키텍처·TDD·가드레일·스타일 규약)
- [ ] `src/voice_agent/adapter/length.py` + `convert_length` 등록(명세·핸들러·토글)
- [ ] 새 도구가 `dispatch_tool` 파이프라인을 지난다
- [ ] `uv run pytest` → **이전(11교시) 개수 + 길이 테스트만큼 증가**, 전체 초록
- [ ] `uv run ruff check src/voice_agent` → **All checks passed!**
- [ ] STEP 5 리뷰 체크리스트를 **사람이 모두 확인**했다

> **계층 규칙 자가 점검**: AI가 만든 코드도 사람이 짠 것과 **같은 기준**으로 검사합니다. 계층·가드레일·테스트를 지나야만 병합합니다.

---

## ⚠️ 자주 나는 오류 & 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| AI가 도메인에 외부 라이브러리 넣음 | 규칙 파일에 계층 규약 부족/미전달 | 규칙 파일 강화 후, 해당 파일을 컨텍스트로 다시 제시 |
| 테스트는 통과하나 가드레일 우회 | 구현이 `dispatch_tool`을 안 지남 | "실행은 dispatch_tool을 거치게" 콕 집어 재요청 |
| AI가 없는 API를 지어냄 | 환각(hallucination) | 실행해 확인, 문서/코드 근거 요구, 안 되면 수동 수정 |
| 엣지 케이스 누락 | 스펙/테스트가 성김 | 스펙에 엣지 케이스 명시 후 테스트부터 다시 |
| "돌아가니까 통과"로 병합 | 리뷰 생략 | STEP 5 체크리스트를 반드시 통과 |
| 기존 테스트가 깨짐 | AI가 공유 코드 변경 | "기존 테스트를 깨지 마라" 규약 + 전체 pytest로 확인 |

---

## 📖 용어 사전 (이 교시 신규)

- **바이브 코딩(vibe coding)**: 자연어 의도로 AI 코딩 에이전트와 함께 코드를 만드는 방식.
- **AI 코딩 에이전트**: 편집기에서 파일을 읽고/쓰고/테스트를 돌리는 AI(예: Copilot Agent Mode, Claude Code).
- **규칙 파일(instructions/agents 파일)**: 코드베이스 규약을 적어 AI가 따르게 하는 문서.
- **스펙 주도 개발(SDD)**: 만들 것을 스펙으로 먼저 정하고 그에 맞춰 구현하는 방식.
- **테스트 먼저(Test-First)**: 실패하는 테스트를 먼저 써서 정답 기준을 고정하는 TDD 원칙.
- **리뷰(review)**: 산출물을 계층·테스트·가드레일 기준으로 사람이 검증하는 단계.
- **환각(hallucination)**: AI가 없는 API·사실을 그럴듯하게 지어내는 현상.

---

## 🎯 필수 미션 — 다음 교시로 가기 전 반드시 완성

직접 해보고, **막히면 접이식 풀이**를 펼치세요.

### 미션 1 (필수) — cm·mi 왕복 정확도

`convert_length`가 cm↔mi 같은 비직관적 변환도 맞는지, AI로 테스트를 추가하고 사람이 기대값을 검토하세요.
- **어디에**: `tests/adapter/test_length.py`
- **왜**: 허브(미터) 경유가 여러 단위에서 정확한지 확인

### 미션 2 (필수) — 규약 위반을 리뷰로 잡기

일부러 "도메인에 두라"고 잘못 지시해 AI가 계층을 침범하게 한 뒤, STEP 5 리뷰로 잡아 "adapter로 옮겨줘"라고 수정 요청하세요.
- **왜**: 리뷰가 실제로 방어선 역할을 하는지 체감

> 풀이는 아래 **🧩 필수 미션 — 풀이** 에 접이식으로 있습니다.

### 🟦 선택 (여유 있으면) — 규약 추가 실험

규칙 파일에 "한 함수는 20줄 이하"를 넣고, 같은 기능을 다시 요청해 AI가 더 잘게 쪼개는지 관찰하세요. 규칙 파일 **어디에·어떻게** 넣는지와 복붙 프롬프트는 아래 **풀이 3**에 있습니다.

---

## 🧩 필수 미션 — 풀이 (막히면 펼치기)

<details>
<summary><strong>📂 풀이 1 — cm·mi 왕복 정확도</strong> &nbsp;<sub>(클릭하여 펼치기)</sub></summary>

**① AI에게 줄 프롬프트 (그대로 복붙)**

```text
tests/adapter/test_length.py 에 convert_length의 왕복 정확도 pytest 테스트를 추가해줘.
- mi → m → mi 왕복이 원래 값과 오차 0.01 이내인지 확인
- cm → m 변환 확인(예: 250cm = 2.5m)
기대값은 1mi ≈ 1609.34m 기준으로. 기존 테스트 스타일과 import를 맞추고,
convert_length 구현은 절대 바꾸지 마(테스트만 추가). 함수 이름은 test_로 시작.
```

**② AI가 만든 테스트(사람 검토용 예시)** — `tests/adapter/test_length.py` 에 추가

```python
def test_mi_to_m_and_back():
    m = convert_length(value=1, from_unit="mi", to_unit="m")
    assert 1600 <= m <= 1620                 # 1mi ≈ 1609.34m
    back = convert_length(value=m, from_unit="m", to_unit="mi")
    assert abs(back - 1) < 0.01              # 되돌리면 대략 1mi


def test_cm_to_m():
    assert convert_length(value=250, from_unit="cm", to_unit="m") == 2.5
```

**③ 검토 포인트(사람이 승인)**: 기대값(1mi≈1609.34m)이 맞는가? 오차 허용치가 과하거나 부족하지 않은가? 구현을 건드리지 않았는가?

**④ 실행** — STEP 4의 미터 허브 방식이면 추가 코드 없이 통과합니다.

```powershell
uv run pytest tests/adapter/test_length.py
```

> 💡 왕복 테스트(변환→역변환→원래값)는 변환 계열 함수의 정확도를 값싸게 검증하는 좋은 습관입니다.

</details>

---

<details>
<summary><strong>📂 풀이 2 — 규약 위반을 리뷰로 잡기</strong> &nbsp;<sub>(클릭하여 펼치기)</sub></summary>

이 미션은 "리뷰가 실제로 방어선이 되는지"를 체감하는 연습입니다. 두 프롬프트를 순서대로 씁니다.

**① 프롬프트 A — 일부러 계층을 어기게 유도 (복붙)**

```text
convert_length의 실제 변환 로직을 src/voice_agent/domain/length.py 에 두고,
거기서 미터 허브 방식으로 구현해줘. TOOL_SPECS/핸들러 등록도 해줘.
```

> AI가 `domain/length.py`를 만들면, STEP 5 리뷰의 **계층 경계** 항목이 걸립니다(도메인은 순수 규칙만이어야 하는데 변환 구현이 들어감).

**② 프롬프트 B — 리뷰에서 잡은 뒤 수정 요청 (복붙)**

```text
방금 코드가 프로젝트 규칙 파일의 '아키텍처' 규약을 위반했어.
계층상 변환 구현은 adapter에 있어야 해(도메인은 순수 규칙만).
- src/voice_agent/adapter/length.py 로 convert_length·SUPPORTED를 옮기고
- src/voice_agent/domain/length.py 는 삭제
- import 경로를 모두 맞추고
- uv run pytest 전체가 초록인지 확인해줘.
규칙 파일의 '## 아키텍처' 항목을 기준으로 판단해.
```

**③ 확인**: 옮긴 뒤 `uv run pytest` 전체가 여전히 초록인지, `domain/`에 IO/변환이 남지 않았는지 사람이 확인합니다.

> 💡 **핵심 교훈**: 테스트가 통과해도 **배치가 틀릴 수** 있습니다. 리뷰(계층 체크)가 그걸 잡습니다. 바이브 코딩에서 리뷰를 생략하면, 겉으론 멀쩡한데 구조가 서서히 무너집니다.

</details>

---

<details>
<summary><strong>📂 풀이 3 (선택) — 규약을 추가하고 AI가 지키는지 관찰</strong> &nbsp;<sub>(클릭하여 펼치기)</sub></summary>

이 미션의 핵심은 **규칙 파일을 고치면 AI 행동이 바뀐다**는 걸 눈으로 확인하는 것입니다. 순서는 (1) 규약 추가 → (2) 같은 기능 재요청 → (3) 결과 비교입니다.

**① 규약을 어디에·어떻게 넣나**

STEP 1에서 만든 **프로젝트 규칙 파일**에 넣습니다. 파일 이름은 쓰는 도구에 따라 다릅니다.

- GitHub Copilot: `.github/copilot-instructions.md`
- Claude Code: 루트의 `CLAUDE.md`
- 그 외 에이전트: 루트의 `AGENTS.md`

그 파일의 **`## 스타일` 섹션 바로 아래**에, 아니면 새 섹션으로 아래 블록을 추가합니다(그대로 복붙).

```markdown
## 코드 크기·복잡도
- 한 함수는 20줄 이하로 유지한다(공백·주석 제외).
- 20줄을 넘으면 의미 있는 단위로 보조 함수를 분리한다.
- 함수 하나는 한 가지 일만 한다(단일 책임).
```

> 💡 **왜 규칙 파일에?** 대화창에 매번 "20줄 이하로 해줘"라고 말할 수도 있지만, 규칙 파일에 넣으면 **이후 모든 요청에 자동 적용**됩니다. 규약은 한 번 쓰고 계속 재사용하는 게 이득입니다.

**② 재요청 프롬프트 (복붙)**

```text
프로젝트 규칙 파일에 '코드 크기·복잡도' 규약을 추가했어(한 함수 20줄 이하, 단일 책임).
그 규약에 맞춰 adapter/length.py의 convert_length를 다시 정리해줘.
- 단위 정규화, 허용 목록 검사, 음수 검증, 변환을 각각 작은 보조 함수로 분리
- 공개 함수 convert_length는 그 보조 함수들을 조합만
- 동작과 기존 테스트 결과는 그대로(리팩터, 초록 유지)
규칙 파일의 '## 코드 크기·복잡도'를 기준으로 판단해.
```

**③ 관찰·검토**

- AI가 `_normalize`, `_check_supported`, `_to_meters` 같은 **보조 함수로 쪼갰는가?**
- `convert_length` 본문이 짧아지고 **조합만** 하는가?
- `uv run pytest`가 **여전히 초록**인가?(동작 불변) `uv run ruff check`도 통과하는가?

> 💡 규약 추가 전/후의 결과물을 비교해 보세요. 같은 요청인데 코드 구조가 달라졌다면, **규칙 파일이 실제로 AI를 통제한다**는 증거입니다. 앞으로 팀 컨벤션(명명·에러 처리·로깅 등)을 규칙 파일에 쌓아가면, AI 출력이 점점 팀 스타일에 맞습니다.

</details>

---

### ✅ 미션 완료 확인 (= 진행 게이트)

```powershell
uv run pytest
uv run ruff check src/voice_agent
```

- 전체 테스트 **초록 유지**(기존 + 길이 도구), ruff 통과.
- STEP 5 리뷰 체크리스트를 **모두 사람이 확인**.
- `/`에서 "3km는 몇 미터야?"가 새 도구로 정확히 처리됨.

이 세 가지가 되면 게이트 통과입니다.

---

**다음 교시 예고 — 13교시(바이브 코딩 ②)**: 이번보다 **큰 기능**을 바이브 코딩으로 얹습니다(예: 대화 기록 저장·요약, 또는 웹 자막 표시). 템플릿을 벗어난 기능일수록 **스펙·테스트·리뷰의 규율**이 더 중요해진다는 걸 확인합니다.
> **선행**: 위 바이브 코딩 ① 게이트(전체 초록 + 리뷰 완료 + 길이 도구 관찰) 통과 상태.
