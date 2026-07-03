import asyncio
import uuid

from fastrtc import AsyncStreamHandler, wait_for_item
from websockets.exceptions import ConnectionClosed

from voice_agent.adapter.async_realtime import AsyncRealtimeSession
from voice_agent.adapter.async_websocket import AsyncWebSocketConnection
from voice_agent.adapter.function_call import extract_function_call
from voice_agent.adapter.realtime_tools import build_tools
from voice_agent.adapter.tools import TOOL_SPECS, dispatch_tool   # run_tool·rate_limit_error 대신
from voice_agent.adapter.transcript import (
    extract_error_message,
    extract_transcript_delta,
    extract_user_transcript,
)
from voice_agent.adapter.transcript_store import FileTranscriptStore
from voice_agent.domain.audio_frame import AudioFrame
from voice_agent.domain.conversation import Conversation
from voice_agent.domain.rate_limiter import RateLimiter
from voice_agent.domain.session_config import SessionConfig
from voice_agent.domain.turn import Role, Turn

from voice_agent.adapter.audio_output import decode_audio_delta, is_speech_started
from voice_agent.domain.tool_toggle import ToolToggleState
from voice_agent.infra import transcript_bus
from voice_agent.usecase.list_active_tools import ListActiveTools
from voice_agent.usecase.save_conversation import SaveConversation


class _StaticToolRegistry:
    """TOOL_SPECS를 그대로 돌려주는 레지스트리(3교시 ToolRegistryPort 모양)."""

    def all_specs(self):
        return TOOL_SPECS
    

class RealtimeVoiceHandler(AsyncStreamHandler):
    """마이크 오디오를 Realtime으로 흘려보내고, 응답 자막을 터미널에 출력한다."""

    def __init__(self):
        # 입력 오디오를 24kHz로 받아 Realtime의 24kHz PCM에 맞춘다.
        super().__init__(input_sample_rate=24000)
        self._session: AsyncRealtimeSession | None = None
        self.output_queue: asyncio.Queue = asyncio.Queue()   # ← 재생 큐 추가
        self._response_active = False   # 응답 생성 진행 중 여부

        # 토글: 처음엔 두 도구를 모두 켠 상태로 시작(원하면 하나만 켜도 됨).
        self._toggles = ToolToggleState()
        for name in ("get_current_time", "get_weather", "calculate", "convert_currency", "convert_temperature", "convert_length"):
            self._toggles.toggle(name)                      # 도구 모두 켜기
        # 도구별로 10초에 5번까지 허용(남용·반복 호출 방지).
        self._limiter = RateLimiter(max_calls=5, window_seconds=10)

        # 대화 저장: 이번 세션의 대화를 턴으로 모았다가 종료 시 파일로 남긴다.
        self._conversation = Conversation()
        self._assistant_buffer = ""                       # 진행 중 어시스턴트 자막 조각들
        self._session_id = uuid.uuid4().hex[:8]           # 세션 식별자
        self._save = SaveConversation(store=FileTranscriptStore(directory="transcripts"))

    def copy(self) -> "RealtimeVoiceHandler":
        # 접속자마다 새 핸들러 인스턴스
        return RealtimeVoiceHandler()

    async def start_up(self) -> None:
        # Realtime에 연결하고 오디오 세션을 연 뒤, 이벤트 읽기 루프를 돈다.
        # (start_up은 스트림당 한 번 호출되며, 여기서 계속 이벤트를 읽어도 된다.)
        config = SessionConfig()
        conn = await AsyncWebSocketConnection.connect(model=config.model)
        self._session = AsyncRealtimeSession(connection=conn)

        # 1) 토글로 켜진 도구 명세만 고른다(3교시 유즈케이스 재사용).
        active_specs = ListActiveTools(registry=_StaticToolRegistry()).execute(self._toggles)
        # 2) 명세를 Realtime 함수 정의 JSON으로 변환.
        tools = build_tools(active_specs)
        # 3) 도구를 실은 채로 세션을 연다.
        await self._session.open(config, tools=tools)

        print(f"[연결됨] 도구 {len(tools)}개 활성", flush=True)
        await self._read_events()

    async def _barge_in(self) -> None:
        # 사용자가 끼어들면, 아직 재생 안 한 오디오를 전부 버린다.
        # 1) 우리 재생 큐를 완전히 비운다(get_nowait로 하나씩 꺼내 버림).
        while not self.output_queue.empty():
            self.output_queue.get_nowait()
        # 2) FastRTC가 이미 전송하려고 쥐고 있는 내부 출력 버퍼도 비운다.
        self.clear_queue()   # 둘 다 비워야 소리가 '뚝' 끊긴다

        # 실제로 응답이 진행 중일 때만 취소 (헛된 취소 → no active response 방지)
        if self._response_active and self._session is not None:
            await self._session.cancel_response()
            self._response_active = False

    async def _read_events(self) -> None:
        # 자막·오류를 헬퍼로 판정하고, 핸들러는 출력만 맡는다.
        try:
            async for event in self._session.events():
                await self._process_event(event)
        except ConnectionClosed:
            # 중지/새로고침 등으로 세션이 닫히면 조용히 종료 (정상 상황)
            print("[종료] 세션이 닫혔습니다", flush=True)

    async def _process_event(self, event: dict) -> None:
        # 이벤트 하나를 종류별로 판정해 알맞은 헬퍼에 넘긴다.
        self._track_response_state(event)
        if self._emit_transcript(event):
            return
        if self._emit_user_transcript(event):
            return
        if self._emit_audio(event):
            return
        if is_speech_started(event):
            await self._barge_in()
            return
        fc = extract_function_call(event)
        if fc is not None:
            await self._handle_tool_call(fc)
            return
        self._emit_error_or_done(event)

    def _track_response_state(self, event: dict) -> None:
        # 응답 생성 진행 상태 추적
        etype = event.get("type")
        if etype == "response.created":
            self._response_active = True
        elif etype == "response.done":
            self._response_active = False
            print(flush=True)
            self._finalize_assistant_turn()

    def _finalize_assistant_turn(self) -> None:
        # 한 응답이 끝나면 모아둔 자막을 어시스턴트 턴으로 확정한다.
        if self._assistant_buffer.strip():
            self._conversation.add_turn(Turn(role=Role.ASSISTANT, text=self._assistant_buffer.strip()))
        self._assistant_buffer = ""

    def _emit_transcript(self, event: dict) -> bool:
        # 자막: 텍스트 조각이면 화면에 출력한다. 처리했으면 True.
        text = extract_transcript_delta(event)
        if not text:
            return False
        print(text, end="", flush=True)
        transcript_bus.publish(text)   # ← 브라우저로도 방송
        self._assistant_buffer += text   # 대화 저장용으로 조각을 모은다
        return True

    def _emit_user_transcript(self, event: dict) -> bool:
        # 사용자 입력 전사 완료: 완성된 문장을 바로 사용자 턴으로 기록한다.
        text = extract_user_transcript(event)
        if text is None:
            return False
        if text.strip():
            self._conversation.add_turn(Turn(role=Role.USER, text=text.strip()))
        return True

    def _emit_audio(self, event: dict) -> bool:
        # 음성: base64 PCM을 디코드해 재생 큐에 넣는다. 처리했으면 True.
        #   put_nowait: 기다리지 않고 즉시 큐에 넣기(생산자 역할).
        #   reshape(1, -1): (N,) 1차원을 (1, N) 2차원(모노 한 채널)으로.
        audio = decode_audio_delta(event)
        if audio is None:
            return False
        self.output_queue.put_nowait((24000, audio.reshape(1, -1)))
        return True

    def _emit_error_or_done(self, event: dict) -> None:
        # 오류 / 응답 끝 (오류는 5교시 헬퍼로 판정)
        error = extract_error_message(event)
        if error:
            print(f"\n[오류] {error}", flush=True)
        elif event.get("type") == "response.done":
            print(flush=True)
            transcript_bus.publish("")   # ← 브라우저로도 방송

    async def receive(self, frame) -> None:
        # FastRTC가 마이크 프레임이 올 때마다 호출한다.
        # frame = (sample_rate, numpy 배열) 튜플.
        if self._session is None:
            return   # 아직 연결 준비 전이면 조용히 건너뜀
        sample_rate, array = frame
        # numpy 오디오 배열을 Realtime이 원하는 'PCM16 바이트'로 변환한다:
        #   .squeeze()        : (1, N) 같은 불필요한 차원을 없애 1차원으로
        #   .astype("<i2")    : 리틀엔디언 16비트 정수(int16)로 형변환 ("<"=리틀엔디언, "i2"=2바이트 정수)
        #   .tobytes()        : 숫자 배열을 실제 바이트열로
        pcm = array.squeeze().astype("<i2").tobytes()
        # AudioFrame(도메인 값객체)에 담아 세션으로 보낸다.
        await self._session.send_audio(AudioFrame(sample_rate=sample_rate, data=pcm))

    async def _handle_tool_call(self, fc: dict) -> None:
        # 가드레일 파이프라인 한 줄: 빈도 → 존재 → 인자 → 실행을 한 번에.
        output = dispatch_tool(self._limiter, fc["name"], fc["arguments"])
        print(f"\n[도구] {fc['name']}({fc['arguments']}) → {output}", flush=True)
        # 결과(정상이든 에러든)를 모델에 돌려주고 최종 응답을 요청.
        await self._session.send_tool_result(call_id=fc["call_id"], output=output)
        await self._session.request_response()
        
    async def emit(self):
        # ⚠️ 중요: emit은 반드시 await로 이벤트 루프에 '양보'해야 한다.
        # 그냥 return None 하면 루프가 굶어 start_up의 연결까지 멈춘다(FastRTC 함정).
        # FastRTC가 '스피커로 보낼 오디오'가 필요할 때 반복 호출한다(소비자 역할).
        # wait_for_item: 큐에 항목이 있으면 꺼내 주고, 없으면 잠깐 기다렸다 None을 준다.
        #   → 내부적으로 await(양보)하므로, 5교시의 sleep 없이도 루프가 굶지 않는다.
        return await wait_for_item(self.output_queue)

    async def shutdown(self) -> None:
        if self._session is not None:
            await self._session.close()
        # 부수효과는 조용히: 저장 실패해도 세션 종료는 정상 진행.
        try:
            summary = self._save.execute(self._conversation, self._session_id)
            print(f"\n[저장됨] transcripts/{self._session_id}.md · {summary}", flush=True)
        except OSError as exc:
            print(f"\n[저장 실패] {exc}", flush=True)