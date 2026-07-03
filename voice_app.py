from modulefinder import test

import gradio as gr
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse       # HTML 문자열을 응답으로 돌려주는 도구
from fastapi.staticfiles import StaticFiles      # 폴더의 파일을 그대로 서빙하는 도구
from pathlib import Path                         # 파일 경로를 다루는 표준 도구

from fastrtc import Stream
from voice_agent.infra.voice_handler import RealtimeVoiceHandler

from fastapi.responses import StreamingResponse
from voice_agent.infra import transcript_bus


load_dotenv()   # .env의 OPENAI_API_KEY 로딩

# 5·6교시에서 만든 핸들러로 오디오 스트림을 구성(양방향 오디오).
stream = Stream(
    handler=RealtimeVoiceHandler(),
    modality="audio",
    mode="send-receive",
)

app = FastAPI()
stream.mount(app)                                    # /webrtc/offer 등 WebRTC 엔드포인트를 붙인다
app.mount("/static", StaticFiles(directory="static"), name="static")   # /static/* → static 폴더의 파일(app.js 등)
app = gr.mount_gradio_app(app, stream.ui, path="/ui")   # (선택) 기본 Gradio UI를 /ui 에 남겨 비교용


@app.get("/")        # 루트(/)로 접속하면
def index():
    # static/index.html 파일을 읽어 그대로 브라우저에 돌려준다(UTF-8로 읽어 한글 안 깨지게).
    html = Path("static/index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/transcript")
async def transcript_stream():
    async def gen():
        q = transcript_bus.subscribe()
        try:
            while True:
                text = await q.get()
                if text == "":
                    yield f"data: [[TURN]]\n\n"
                else:
                    safe = text.replace("\n", " ")
                    yield f"data: {safe}\n\n"
        finally:
            transcript_bus.unsubscribe(q)
    return StreamingResponse(gen(), media_type="text/event-stream")