[VoxAttend_README.md](https://github.com/user-attachments/files/29243003/VoxAttend_README.md)
# 🎙️ VoxAttend — AI-Powered Voice Attendance System

A smart classroom attendance system built with **Python (Flask)** that uses **voice recognition** to verify student identity and mark attendance — no apps to install, no proxies possible.

---

## ✨ Features

### 👨‍🏫 Teacher Side
- **Secure Login** — Password-protected teacher dashboard
- **Student Registration** — Add students by roll number and name with voice profile capture
- **QR Session Generator** — Creates a unique session ID (valid for 60 seconds) with a live countdown timer
- **Live Attendance Stats** — Real-time present/absent count and attendance rate
- **Voice Query Dashboard** — Ask questions like *"How many students are present?"* or *"Who is absent?"* by voice or text
- **Weekly Summary** — 7-day attendance report with best/worst day and average rate
- **Leaderboard** — Top students ranked by total attendance days
- **Parent Alerts** — Auto-generates alert messages for students absent 3+ consecutive days
- **Finalize Absents** — One-click to mark all non-verified students as absent

### 👨‍🎓 Student Side
- **QR Code Scan** — Enter the session ID from the teacher's QR
- **Live Challenge System** — Random anti-proxy challenge (math question, phrase repeat, or today's date)
- **Voice Verification** — Student speaks the answer; browser captures and verifies speech
- **Mood Tracker** — Students log their mood (Good / Okay / Tired) when marking attendance
- **Streak Tracking** — Rewards consecutive attendance days with encouraging messages
- **Bilingual Confirmation** — Attendance confirmation spoken in Hindi + English via Murf AI TTS

### 🔒 Anti-Proxy Protection
- Session expires in 60 seconds
- Random live challenge every session — can't be pre-recorded
- 2 failed attempts = automatic disqualification from the session
- Voice similarity check using cosine similarity on voice embeddings

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Backend logic |
| Flask | Web framework & REST API |
| NumPy | Voice embedding & cosine similarity |
| Web Speech API | Browser-based voice recognition (no install needed) |
| Murf AI API | Text-to-speech confirmation (Hindi + English) |
| QRCode.js | QR code generation in browser |
| HTML / CSS / JS | Frontend UI with dark glassmorphism theme |
| Heroku | Deployment |

---

## 📁 Project Structure

```
voice-attendance-main/
├── app.py                  # Main Flask app — all routes & logic
├── requirements.txt        # Python dependencies
├── Procfile                # Heroku deployment config
├── .env                    # Environment variables (API keys)
├── static/
│   ├── css/
│   │   └── style.css       # Dark glassmorphism UI styles
│   └── js/
│       └── murf.js         # Murf AI TTS integration
├── templates/
│   ├── index.html          # Home / landing page
│   ├── teacher_login.html  # Teacher login page
│   ├── teacher.html        # Teacher dashboard
│   ├── student.html        # Student attendance page
│   └── register.html       # Student registration page
├── fix_register.py         # Mobile recording fix utility
├── fix_student.py          # Student page fix utility
└── fix_teacher.py          # Teacher page fix utility
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- A [Murf AI](https://murf.ai) API key (for voice TTS)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/vshnuupriyaa-maker/voice-attendance.git

# 2. Navigate into the project folder
cd voice-attendance-main

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create a .env file with the following:
MURF_API_KEY=your_murf_api_key_here
TEACHER_PASSWORD=your_teacher_password_here

# 5. Run the app
python app.py
```

Then open [http://localhost:10000](http://localhost:10000) in your browser.

---

## 🌐 Deployment (Heroku)

This project is deployed on **Heroku** using the included `Procfile`.

```bash
heroku create your-app-name
heroku config:set MURF_API_KEY=your_key_here
heroku config:set TEACHER_PASSWORD=your_password_here
git push heroku main
```

Live URL: _add your Heroku URL here_

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/teacher-login` | Teacher authentication |
| POST | `/api/register-student` | Register a new student |
| GET | `/api/student-list` | List all registered students |
| POST | `/api/delete-student` | Remove a student |
| POST | `/api/start-session` | Start a new attendance session |
| POST | `/api/validate-session` | Validate a session ID |
| GET | `/api/challenge` | Get a random anti-proxy challenge |
| POST | `/api/verify` | Submit voice + verify attendance |
| POST | `/api/mood` | Log student mood |
| POST | `/api/teacher-query` | Voice/text query for stats |
| POST | `/api/mark-absents` | Finalize and mark absents |
| GET | `/api/weekly-summary` | 7-day attendance summary |
| GET | `/api/leaderboard` | Get attendance leaderboard |
| POST | `/api/speak` | Text-to-speech via Murf AI |

---

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `MURF_API_KEY` | Your Murf AI API key for TTS |
| `TEACHER_PASSWORD` | Password to access teacher dashboard (default: `teacher123`) |

> ⚠️ Never commit your `.env` file to GitHub. It is already in `.gitignore`.

---

## 👩‍💻 Built By

**Arava Vishnu Priya Gopi**  
GitHub: [@vshnuupriyaa-maker](https://github.com/vshnuupriyaa-maker)
