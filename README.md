# SpeakWise AI — AI Conversational Partner for Regional Language Learning

SpeakWise AI is an intelligent full-stack web application designed to help learners build English communication confidence through real-time conversational practice, voice interaction, and grammar and fluency analysis.

---

## 🚀 Live Deployments

- **Frontend (Vercel)**: [https://speak-wise-ai-five.vercel.app](https://speak-wise-ai-five.vercel.app)
- **Backend (Render)**: [https://speakwise-ai-1.onrender.com](https://speakwise-ai-1.onrender.com)
- **GitHub Repository**: [https://github.com/mdrehantabish07/SpeakWise-AI.git](https://github.com/mdrehantabish07/SpeakWise-AI.git)

---

## 🛠️ Architecture & Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 (Inter typography, glassmorphism, responsive navigation), JavaScript ES6+
- **Voice & Audio**: Web Speech Recognition API (`SpeechRecognition`) & Web Speech Synthesis API (`SpeechSynthesis`) with Hindi and English voice selection
- **Backend API**: FastAPI, Uvicorn, Pydantic, official `openai` Python SDK
- **AI Model**: `CohereLabs/aya-expanse-32b:cohere` via Hugging Face Router (`https://router.huggingface.co/v1`)
- **Analysis Engine**: Built-in SpeakWise linguistic and grammatical analysis pipeline (`speakwise_engine.py`)
- **Authentication**: Firebase Authentication (Google Sign-In & Phone OTP)

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Application status, model identifier, and frontend serving |
| `GET` | `/health`, `/api/health` | Health check reporting service status & HF configuration |
| `POST` | `/chat`, `/api/chat` | AI conversational completions via Hugging Face router |
| `POST` | `/analyze`, `/api/analyze` | Linguistic and grammatical sentence analysis |

---

## 🏃 Run Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your Hugging Face API token:
```env
HF_TOKEN=your_huggingface_token_here
```
*(Ensure your Hugging Face account has inference credits configured at [https://huggingface.co/settings/billing](https://huggingface.co/settings/billing) for live AI chat).*

### 3. Start Backend & Frontend Server
```bash
python launcher.py
```
Or run backend directly:
```bash
uvicorn backend.main:app --reload --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in Google Chrome or any modern browser.

---

## ⚠️ AI Provider Credit Notice

Hugging Face Inference Providers require pre-paid account credits or a Hugging Face PRO subscription. If credits are exhausted, the backend returns an explicit `HTTP 402 Payment Required` status, which the frontend displays clearly with retry controls.