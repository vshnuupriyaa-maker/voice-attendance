f = open('templates/register.html', 'w', encoding='utf-8')
f.write("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Register Student</title>
<link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
<div class="container">
  <header>
    <a href="/" class="back-btn">Home</a>
    <h1>Register Student Voice</h1>
  </header>

  <div class="panel">
    <h2>Step 1 — Enter Your Name</h2>
    <input type="text" id="reg-name" placeholder="Type your full name here"/>
  </div>

  <div class="panel">
    <h2>Step 2 — Record Your Voice</h2>
    <div class="instruction-box">
      <p>Click record and say clearly:</p>
      <div class="say-this">"My name is [Your Name] and I am registering my voice"</div>
    </div>
    <button class="btn btn-mic btn-large" id="reg-record-btn" onclick="startRegRecording()">Start Recording</button>
    <div class="record-status hidden" id="reg-record-status">
      <div class="pulse-ring"></div>
      <span>Recording... speak now</span>
    </div>
    <div class="transcript-box" id="reg-transcript">Your words will appear here...</div>
  </div>

  <div class="panel hidden" id="save-panel">
    <h2>Step 3 — Save Registration</h2>
    <button class="btn btn-primary btn-large" onclick="saveRegistration()">Save My Voice</button>
    <div class="response-box" id="reg-response"></div>
  </div>

  <div class="panel">
    <h2>Registered Students</h2>
    <button class="btn btn-secondary" onclick="loadStudents()">Refresh</button>
    <div id="reg-students-list" style="margin-top:1rem"></div>
  </div>
</div>
<script>
let regAudioBlob = null;
let regMediaRecorder = null;
let regAudioChunks = [];
let regSpokenText = "";

async function startRegRecording() {
  const name = document.getElementById("reg-name").value.trim();
  if (!name) { alert("Please enter your name first!"); return; }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Speech recognition
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.lang = "en-IN";
      recognition.onresult = (e) => {
        regSpokenText = e.results[0][0].transcript;
        document.getElementById("reg-transcript").textContent = regSpokenText;
      };
      recognition.start();
    }

    // Audio recording
    regMediaRecorder = new MediaRecorder(stream);
    regAudioChunks = [];
    regMediaRecorder.ondataavailable = (e) => regAudioChunks.push(e.data);
    regMediaRecorder.onstop = () => {
      regAudioBlob = new Blob(regAudioChunks, { type: "audio/webm" });
      document.getElementById("save-panel").classList.remove("hidden");
      document.getElementById("reg-record-status").classList.add("hidden");
      document.getElementById("reg-record-btn").textContent = "Record Again";
      document.getElementById("reg-record-btn").onclick = startRegRecording;
    };
    regMediaRecorder.start();
    document.getElementById("reg-record-btn").textContent = "Stop Recording";
    document.getElementById("reg-record-btn").onclick = stopRegRecording;
    document.getElementById("reg-record-status").classList.remove("hidden");
    setTimeout(stopRegRecording, 5000);

  } catch(e) {
    alert("Microphone access denied! Please allow microphone.");
  }
}

function stopRegRecording() {
  if (regMediaRecorder && regMediaRecorder.state !== "inactive") {
    regMediaRecorder.stop();
  }
}

async function saveRegistration() {
  const name = document.getElementById("reg-name").value.trim();
  if (!name) { alert("Please enter your name!"); return; }

  let audioB64 = "";
  if (regAudioBlob) {
    const buf = await regAudioBlob.arrayBuffer();
    audioB64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
  }

  const res = await fetch("/api/register-student", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: name,
      audio: audioB64,
      spoken_text: regSpokenText
    })
  });

  const data = await res.json();
  const responseBox = document.getElementById("reg-response");

  if (data.success) {
    responseBox.textContent = "✅ " + data.message;
    responseBox.style.color = "#4ade80";
    document.getElementById("reg-name").value = "";
    document.getElementById("reg-transcript").textContent = "Your words will appear here...";
    document.getElementById("save-panel").classList.add("hidden");
    regAudioBlob = null;
    regSpokenText = "";
    loadStudents();
  } else {
    responseBox.textContent = "❌ " + data.reason;
    responseBox.style.color = "#ef4444";
  }
}

async function loadStudents() {
  const res = await fetch("/api/student-list");
  const data = await res.json();
  const list = document.getElementById("reg-students-list");
  if (data.students.length === 0) {
    list.innerHTML = "<p style='color:#94a3b8'>No students registered yet</p>";
    return;
  }
  list.innerHTML = data.students.map((s, i) =>
    "<div class='leader-row'>" +
    "<span class='medal'>" + (i+1) + "</span>" +
    "<span class='leader-name'>" + s.name + "</span>" +
    "<span style='font-size:0.82rem;color:" + (s.has_voice ? "#4ade80" : "#f59e0b") + "'>" +
    (s.has_voice ? "✅ Voice Registered" : "⚠️ No Voice") + "</span>" +
    "<button style='margin-left:8px;padding:4px 10px;background:#ef4444;color:white;border:none;border-radius:8px;cursor:pointer' onclick='deleteStudent(\"" + s.name + "\")'>Remove</button>" +
    "</div>"
  ).join("");
}

async function deleteStudent(name) {
  if (!confirm("Remove " + name + "?")) return;
  await fetch("/api/delete-student", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
  loadStudents();
}

loadStudents();
</script>
</body>
</html>""")
f.close()
print("register.html created!")