const toggle = document.getElementById("toggle");
const audioEl = document.getElementById("audio");
const statusText = document.getElementById("statusText");
const dot = document.getElementById("dot");

let pc = null;
let localStream = null;

function setStatus(text, live = false) {
  statusText.textContent = text;
  dot.classList.toggle("live", live);
}

async function start() {
  setStatus("연결 중...");
  // RTCPeerConnection: 브라우저의 WebRTC 연결 객체. 이 안에서 협상·미디어가 오간다.
  pc = new RTCPeerConnection();
  // webrtc_id: 이 연결을 식별하는 임의의 문자열. offer·ICE를 서버가 같은 연결로 묶는 데 쓴다.
  const webrtc_id = Math.random().toString(36).substring(7);

  // 1) 서버(FastRTC)가 보내는 음성 트랙이 도착하면(track 이벤트) <audio>에 연결해 재생.
  pc.addEventListener("track", (evt) => {
    if (audioEl.srcObject !== evt.streams[0]) {   // 중복 설정 방지
      audioEl.srcObject = evt.streams[0];         // 받은 스트림을 스피커로
    }
  });

  // 2) 마이크 입력을 얻어 연결에 추가한다(send-receive: 보내고+받고).
  //    echoCancellation/noiseSuppression: 되울림·잡음을 줄여 피드백 루프를 막는다.
  localStream = await navigator.mediaDevices.getUserMedia({
    audio: { echoCancellation: true, noiseSuppression: true },
  });
  // 마이크의 각 트랙을 연결에 얹는다 → 서버로 내 음성이 전송된다.
  localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));

  // 3) 데이터 채널 — FastRTC 핸드셰이크에 필수! (없으면 연결이 시작되지 않음)
  //    이름은 반드시 "text". 실제로 이 채널로 데이터를 보내지 않아도, 존재 자체가 필요하다.
  const dataChannel = pc.createDataChannel("text");

  // 연결 상태가 바뀔 때마다 화면 표시를 갱신한다.
  pc.onconnectionstatechange = () => {
    if (pc.connectionState === "connected") setStatus("대화 중", true);   // 연결됨 → 초록
    else if (["failed", "disconnected", "closed"].includes(pc.connectionState))
      setStatus("연결 종료");
  };

  // 4) ICE 후보를 찾는 족족 서버로 '트리클' 전송(방화벽 뒤에서도 경로를 찾게).
  //    브라우저가 후보를 하나 찾을 때마다 onicecandidate가 호출된다.
  pc.onicecandidate = ({ candidate }) => {
    if (candidate) {   // candidate가 null이면 '수집 끝' 신호이므로 무시
      fetch("/webrtc/offer", {                        // offer와 같은 엔드포인트로 보낸다
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate: candidate.toJSON(),              // 후보를 JSON으로 직렬화
          webrtc_id: webrtc_id,                       // 어느 연결의 후보인지 식별
          type: "ice-candidate",                      // 이 POST가 'ICE 후보'임을 표시
        }),
      });
    }
  };

  // 5) SDP offer(내 연결 사양서)를 만들고 → 서버로 POST → 서버의 answer를 설정.
  const offer = await pc.createOffer();               // 제안서 생성
  await pc.setLocalDescription(offer);                // 내 쪽 사양으로 확정(이때부터 ICE 수집 시작)
  const res = await fetch("/webrtc/offer", {          // 서버로 offer 전송
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sdp: offer.sdp,                                 // 실제 사양서 본문
      type: offer.type,                               // "offer"
      webrtc_id: webrtc_id,                           // 연결 식별자
    }),
  });
  const answer = await res.json();                    // 서버의 응답서(answer)를 받아
  await pc.setRemoteDescription(answer);              // 상대 쪽 사양으로 설정 → 핸드셰이크 완료, 오디오 흐름 시작

  // 자막 스트림 구독 (서버 → 브라우저)
  const es = new EventSource("/transcript");
  const box = document.getElementById("transcript");
  es.onmessage = (e) => { 
    if (e.data === "[[TURN]]") {  // turn이 바뀌면 줄바꿈
      box.innerHTML += "<br><br>";
    } else {
      box.appendChild(document.createTextNode(e.data));  // 새 자막을 추가
    }
    box.scrollTop = box.scrollHeight;  // 스크롤을 맨 아래로 
  };
  // stop()에서 es.close()도 호출하도록 es를 바깥 변수로 두면 더 깔끔합니다.
}

function stop() {
  if (pc) { pc.close(); pc = null; }                  // 연결을 닫고 비운다
  if (localStream) { localStream.getTracks().forEach((t) => t.stop()); localStream = null; }  // 마이크 해제
  setStatus("대기 중");
}

toggle.addEventListener("click", async () => {
  if (toggle.classList.contains("on")) {
    stop();
    toggle.classList.remove("on");
    toggle.textContent = "대화 시작";
  } else {
    toggle.classList.add("on");
    toggle.textContent = "중지";
    try {
      await start();
    } catch (err) {
      let msg = "연결에 실패했어요. 잠시 후 다시 시도해 주세요.";
      if (err.name === "NotAllowedError") msg = "마이크 권한이 필요해요. 브라우저 주소창의 🎙️ 아이콘에서 허용해 주세요.";
      else if (err.name === "NotFoundError") msg = "마이크를 찾을 수 없어요. 장치 연결을 확인해 주세요.";
      setStatus(msg);
      toggle.classList.remove("on");
      toggle.textContent = "대화 시작";
    }
  }
});