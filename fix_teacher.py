f = open('templates/teacher.html', 'w', encoding='utf-8')
f.write("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Teacher Dashboard</title>
<link rel="stylesheet" href="/static/css/style.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
</head>
<body>
<div class="container">
  <header>
    <a href="/" class="back-btn">Home</a>
    <h1>Teacher Dashboard</h1>
  </header>
  <div class="panel">
    <h2>Attendance Session</h2>
    <button class="btn btn-primary btn-large" id="startbtn">Start Attendance Session</button>
    <div id="qr-section" style="display:none;margin-top:1rem">
      <div class="qr-wrapper">
        <div id="qr-code"></div>
        <div class="session-info">
          <div class="session-id" id="session-id-display"></div>
          <div class="timer-bar-wrap"><div class="timer-bar" id="timer-bar"></div></div>
          <div class="timer-text" id="timer-text">60s remaining</div>
        </div>
      </div>
      <button class="btn btn-secondary" id="newqrbtn">Generate New QR</button>
    </div>
  </div>
  <div class="panel">
    <h2>Live Attendance</h2>
    <div class="stats-grid">
      <div class="stat-card stat-present"><div class="stat-num" id="present-count">0</div><div class="stat-label">Present</div></div>
      <div class="stat-card stat-absent"><div class="stat-num" id="absent-count">0</div><div class="stat-label">Absent</div></div>
      <div class="stat-card stat-pct"><div class="stat-num" id="pct-count">0%</div><div class="stat-label">Rate</div></div>
    </div>
    <div id="present-list" style="margin-top:1rem"></div>
    <button class="btn btn-secondary" id="refreshbtn">Refresh Stats</button>
    <button class="btn btn-warning" id="absentbtn">Finalize and Mark Absents</button>
  </div>
  <div class="panel">
    <h2>Voice Query Dashboard</h2>
    <div class="voice-examples">
      <span id="q1">How many present?</span>
      <span id="q2">Who is absent?</span>
      <span id="q3">Mood report</span>
      <span id="q4">Show leaderboard</span>
    </div>
    <div class="voice-input-row">
      <button class="btn btn-mic" id="micbtn">Speak Query</button>
      <input type="text" id="query-input" placeholder="Or type your query..."/>
      <button class="btn btn-primary" id="askbtn">Ask</button>
    </div>
    <div class="response-box" id="query-response"></div>
  </div>
  <div class="panel">
    <h2>Weekly Summary</h2>
    <button class="btn btn-primary" id="weeklybtn">Get Voice Summary</button>
    <div id="weekly-chart" class="weekly-chart"></div>
  </div>
  <div class="panel">
    <h2>Leaderboard</h2>
    <button class="btn btn-secondary" id="lbbtn">Refresh</button>
    <div id="leaderboard-list" class="leaderboard-list"></div>
  </div>
  <div class="panel" id="alerts-panel" style="display:none">
    <h2>Parent Alerts</h2>
    <div id="alerts-list"></div>
  </div>
</div>
<script src="/static/js/murf.js"></script>
<script>
var currentSessionId = null;
var timerInterval = null;

document.getElementById("startbtn").addEventListener("click", startSession);
document.getElementById("newqrbtn").addEventListener("click", startSession);
document.getElementById("refreshbtn").addEventListener("click", refreshStats);
document.getElementById("absentbtn").addEventListener("click", markAbsents);
document.getElementById("askbtn").addEventListener("click", askQuery);
document.getElementById("weeklybtn").addEventListener("click", getWeeklySummary);
document.getElementById("lbbtn").addEventListener("click", loadLeaderboard);
document.getElementById("micbtn").addEventListener("click", startVoice);
document.getElementById("q1").addEventListener("click", function() { document.getElementById("query-input").value = "How many students are present?"; });
document.getElementById("q2").addEventListener("click", function() { document.getElementById("query-input").value = "Who is absent today?"; });
document.getElementById("q3").addEventListener("click", function() { document.getElementById("query-input").value = "What is the mood report?"; });
document.getElementById("q4").addEventListener("click", function() { document.getElementById("query-input").value = "Show leaderboard"; });

async function startSession() {
  var res = await fetch("/api/start-session", { method: "POST" });
  var data = await res.json();
  currentSessionId = data.session_id;
  document.getElementById("qr-section").style.display = "block";
  document.getElementById("session-id-display").textContent = "Session: " + data.session_id;
  document.getElementById("qr-code").innerHTML = "";
  new QRCode(document.getElementById("qr-code"), {
    text: data.session_id, width: 200, height: 200,
    colorDark: "#1a1a2e", colorLight: "#ffffff"
  });
  startTimer(60);
  await speak("Attendance session started. Session ID is " + data.session_id + ". Students please scan the QR code now.");
}

function startTimer(seconds) {
  if (timerInterval) clearInterval(timerInterval);
  var remaining = seconds;
  var bar = document.getElementById("timer-bar");
  var text = document.getElementById("timer-text");
  timerInterval = setInterval(function() {
    remaining--;
    bar.style.width = ((remaining / seconds) * 100) + "%";
    bar.style.background = remaining > 20 ? "#4ade80" : remaining > 10 ? "#fb923c" : "#f87171";
    text.textContent = remaining + "s remaining";
    if (remaining <= 0) {
      clearInterval(timerInterval);
      text.textContent = "Session expired";
      speak("The QR code has expired. Generate a new one if needed.");
    }
  }, 1000);
}

async function refreshStats() {
  try {
    var studRes = await fetch("/api/student-list");
    var studData = await studRes.json();
    var total = studData.students.length;
    var lbRes = await fetch("/api/leaderboard");
    var lbData = await lbRes.json();
    var present = lbData.leaderboard.length;
    var absent = total - present;
    document.getElementById("present-count").textContent = present;
    document.getElementById("absent-count").textContent = absent < 0 ? 0 : absent;
    document.getElementById("pct-count").textContent = total > 0 ? Math.round((present/total)*100) + "%" : "0%";
    if (lbData.leaderboard.length > 0) {
      var html = "<p style='color:#94a3b8;font-size:0.85rem;margin-bottom:0.5rem'>Present students:</p>";
      for (var i=0; i<lbData.leaderboard.length; i++) {
        html += "<div style='padding:4px 0;font-size:0.9rem'>✅ " + lbData.leaderboard[i].name + "</div>";
      }
      document.getElementById("present-list").innerHTML = html;
    }
  } catch(e) {}
}

async function markAbsents() {
  var res = await fetch("/api/mark-absents", { method: "POST" });
  var data = await res.json();
  if (data.parent_alerts.length > 0) {
    document.getElementById("alerts-panel").style.display = "block";
    var list = document.getElementById("alerts-list");
    var html = "";
    for (var i=0; i<data.parent_alerts.length; i++) {
      var a = data.parent_alerts[i];
      html += "<div class='alert-card'><strong>" + a.name + "</strong> absent " + a.days + " days</div>";
    }
    list.innerHTML = html;
  }
  await speak("Absents marked. " + data.absents.length + " students are absent today.");
  refreshStats();
}

async function askQuery() {
  var query = document.getElementById("query-input").value;
  if (!query) return;
  var res = await fetch("/api/teacher-query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query })
  });
  var data = await res.json();
  document.getElementById("query-response").textContent = data.response;
  await speak(data.response);
}

function startVoice() {
  if (!window.webkitSpeechRecognition && !window.SpeechRecognition) {
    alert("Speech recognition not supported! Type your query instead.");
    return;
  }
  var SR = window.webkitSpeechRecognition || window.SpeechRecognition;
  var r = new SR();
  r.lang = "en-IN";
  r.onresult = function(e) {
    document.getElementById("query-input").value = e.results[0][0].transcript;
    askQuery();
  };
  r.start();
  document.getElementById("micbtn").textContent = "Listening...";
  r.onend = function() { document.getElementById("micbtn").textContent = "Speak Query"; };
}

async function getWeeklySummary() {
  var res = await fetch("/api/weekly-summary");
  var data = await res.json();
  var html = "";
  for (var i=0; i<data.days.length; i++) {
    var d = data.days[i];
    var color = d.percentage > 70 ? "#4ade80" : d.percentage > 40 ? "#fb923c" : "#f87171";
    html += "<div class='week-bar-wrap'>";
    html += "<div class='week-bar' style='height:" + d.percentage + "px;background:" + color + "'></div>";
    html += "<div class='week-label'>" + d.day.slice(0,3) + "</div>";
    html += "<div class='week-pct'>" + d.percentage + "%</div>";
    html += "</div>";
  }
  document.getElementById("weekly-chart").innerHTML = html;
  await speak(data.summary);
}

async function loadLeaderboard() {
  var res = await fetch("/api/leaderboard");
  var data = await res.json();
  var medals = ["1st","2nd","3rd"];
  var html = "";
  if (data.leaderboard.length === 0) {
    html = "<p style='color:#94a3b8'>No data yet</p>";
  } else {
    for (var i=0; i<Math.min(data.leaderboard.length,5); i++) {
      var e = data.leaderboard[i];
      html += "<div class='leader-row'>";
      html += "<span class='medal'>" + (medals[i] || (i+1)+".") + "</span>";
      html += "<span class='leader-name'>" + e.name + "</span>";
      html += "<span class='leader-days'>" + e.days + " days streak:" + e.streak + "</span>";
      html += "</div>";
    }
  }
  document.getElementById("leaderboard-list").innerHTML = html;
}

refreshStats();
loadLeaderboard();
</script>
</body>
</html>""")
f.close()
print("teacher.html updated!")