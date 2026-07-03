# 프로젝트 규약 (AI 코딩 에이전트용)

## 코드 크기·복잡도
- 한 함수는 20줄 이하로 유지한다(공백·주석 제외).
- 20줄을 넘으면 의미 있는 단위로 보조 함수를 분리한다.
- 함수 하나는 한 가지 일만 한다(단일 책임).

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
