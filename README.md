# SpeakWise AI - AI English Communication & Learning Platform

SpeakWise AI is an intelligent web application designed to help learners improve their English communication through real-time conversation practice, voice interactions, and deep grammatical and fluency analysis.

---

## 🚀 Quick Start (Run Locally)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional for Hugging Face LLM)
Create a `.env` file in the root directory:
```env
HF_TOKEN=your_huggingface_api_token_here
```
*(If no token is provided, SpeakWise AI uses its built-in rule-based conversation and learning assistant engines).*

### 3. Run the Backend & Frontend Server
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
Open your browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🌐 Web Deployment Options

### 1. Vercel Deployment
The repository is pre-configured with [vercel.json](file:///c:/Users/mdreh/OneDrive/Desktop/SpeakWise-AI/vercel.json):
- Frontend static files are served automatically.
- Serverless Python API routes are mapped from [api/index.py](file:///c:/Users/mdreh/OneDrive/Desktop/SpeakWise-AI/api/index.py).
- Set `HF_TOKEN` in your Vercel Project Environment Variables.

### 2. Firebase Hosting
Configured with [firebase.json](file:///c:/Users/mdreh/OneDrive/Desktop/SpeakWise-AI/firebase.json):
```bash
firebase deploy
```

### 3. Render / Cloud Web Service
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

---

## 🛠️ Tech Stack
- **Frontend**: HTML5, Vanilla CSS3 (with Inter typography & glassmorphic styling), JavaScript ES6+
- **Backend API**: FastAPI, Uvicorn, Pydantic, Hugging Face Inference API
- **NLP & Analysis**: Custom SpeakWise rule engine, subject-verb agreement analyzers, fluency metrics
- **Authentication**: Firebase Auth (Google Sign-In & Phone OTP)