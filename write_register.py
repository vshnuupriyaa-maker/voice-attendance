html = """<!DOCTYPE html>
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
    <h2>Step 1 - Enter Your Name</h2>
    <input type="text" id="reg-name" placeholder="Type your full name here"/>
  </div>
  <div class="panel">
    <h2>Step 2 - Record Your Voice</h2>
    <div class="instruction-box">
      <p>Click record and say clearly:</p>
      <div class="say-this">My name is [Your Name] and I am registering my voice</div>
    </div>
    <button class="btn btn-mic btn-large" id="reg-record-btn" onclick="recordVoice()">Start Recording</button>
    <div class="record-status hidden" id="reg-status">
      <div class="pulse-ring"></div>
      <span>Recording... speak now</span>
    </div>
    <div class="transcript-box" id="reg-transcript">Your words will appear here...</div>
  </div>
  <div class="panel hidden" id="save-panel">
    <h2>Step 3 - Save Registration</h2>
    <button class="btn btn-primary btn-large" onclick="saveVoice()">Save My Voice</button>
    <div class="response-box" id="reg-response"></div>
  </div>
  <div class="panel">
    <h2>Registered Students</h2>
    <button class="btn btn-secondary" onclick="showStudents()">Refresh List</button>
    <div id="students-div" style="margin-top:1rem"></div>
  </div>
</div>
<script>
var audioBlob = null;
var mediaRec = null;
var chunks = [];
var spokenWords = "";

function recordVoice() {
  var name = document.getElementById("reg-name").value.trim();
  if (!name) {
    alert("Please enter your name first!");
    return;
  }
  if (!navigator.mediaDevices) {
    alert("Please use Chrome browser!");
    return;
  }
  navigator.mediaDevices.getUserMedia({ audio: true }).then(function(stream) {
    document.getElementById("reg-record-btn").textContent = "Recording 5 sec...";
    document.getElementById("reg-status").classList.remove("hidden");
    document.getElementById("reg-transcript").textContent = "Listening...";

    try {
      var recog = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recog.lang = "en-IN";
      recog.onresult = function(e) {
        spokenWords = e.results[0][0].transcript;
        document.getElementById("reg-transcript").textContent = spokenWords;
      };
      recog.onerror = function() {
        spokenWords = name;
        document.getElementById("reg-transcript").textContent = "Voice captured!";
      };
      recog.start();
    } catch(e) {
      spokenWords = name;
      document.getElementById("reg-transcript").textContent = "Voice captured!";
    }

    mediaRec = new MediaRecorder(stream);
    chunks = [];
    mediaRec.ondataavailable = function(e) {
      if (e.data.size > 0) chunks.push(e.data);
    };
    mediaRec.onstop = function() {
      audioBlob = new Blob(chunks, { type: "audio/webm" });
      stream.getTracks().forEach(function(t) { t.stop(); });
      document.getElementById("save-panel").classList.remove("hidden");
      document.getElementById("reg-status").classList.add("hidden");
      document.getElementById("reg-record-btn").textContent = "Record Again";
      document.getElementById("reg-record-btn").onclick = recordVoice;
    };
    mediaRec.start();
    document.getElementById("reg-record-btn").onclick = stopVoice;
    setTimeout(stopVoice, 5000);
  }).catch(function(err) {
    alert("Microphone error: " + err.message + ". Please allow microphone access!");
  });
}

function stopVoice() {
  if (mediaRec && mediaRec.state !== "inactive") {
    mediaRec.stop();
  }
}

function saveVoice() {
  var name = document.getElementById("reg-name").value.trim();
  if (!name) { alert("Enter your name!"); return; }
  var audioB64 = "";
  var responseBox = document.getElementById("reg-response");

  function doSave(b64) {
    fetch("/api/register-student", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name, audio: b64, spoken_text: spokenWords })
    }).then(function(r) { return r.json(); }).then(function(data) {
      if (data.success) {
        responseBox.textContent = name + " registered successfully!";
        responseBox.style.color = "#4ade80";
        document.getElementById("reg-name").value = "";
        document.getElementById("reg-transcript").textContent = "Your words will appear here...";
        document.getElementById("save-panel").classList.add("hidden");
        audioBlob = null;
        spokenWords = "";
        showStudents();
      } else {
        responseBox.textContent = "Error: " + data.reason;
        responseBox.style.color = "#ef4444";
      }
    }).catch(function() {
      responseBox.textContent = "Error saving. Try again!";
      responseBox.style.color = "#ef4444";
    });
  }

  if (audioBlob) {
    var reader = new FileReader();
    reader.onload = function(e) {
      var b64 = e.target.result.split(",")[1];
      doSave(b64);
    };
    reader.readAsDataURL(audioBlob);
  } else {
    doSave("");
  }
}

function showStudents() {
  fetch("/api/student-list").then(function(r) { return r.json(); }).then(function(data) {
    var div = document.getElementById("students-div");
    if (data.students.length === 0) {
      div.innerHTML = "<p style='color:#94a3b8'>No students registered yet</p>";
      return;
    }
    div.innerHTML = data.students.map(function(s, i) {
      return "<div class='leader-row'>" +
        "<span class='medal'>" + (i+1) + "</span>" +
        "<span class='leader-name'>" + s.name + "</span>" +
        "<span style='font-size:0.82rem;color:" + (s.has_voice ? "#4ade80" : "#f59e0b") + "'>" +
        (s.has_voice ? "Voice Registered" : "No Voice") + "</span>" +
        "<button style='margin-left:8px;padding:4px 10px;background:#ef4444;color:white;border:none;border-radius:8px;cursor:pointer' onclick='removeStudent(\"" + s.name + "\")'>Remove</button>" +
        "</div>";
    }).join("");
  }).catch(function() {});
}

function removeStudent(name) {
  if (!confirm("Remove " + name + "?")) return;
  fetch("/api/delete-student", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name })
  }).then(function() { showStudents(); }).catch(function() {});
}

showStudents();
</script>
</body>
</html>"""

with open('templates/register.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done! Length:", len(html))