import os
import sys
import re
import logging
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Google Gemini SDK
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

# Configure logging (Never log keys or credentials)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("speakwise.backend")

# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ============================================================
# SPEAKWISE ENGINE & LEARNING ASSISTANT
# ============================================================

try:
    from speakwise_engine import analyze
except ImportError as error:
    logger.warning("speakwise_engine could not be imported: %s", error)
    analyze = None

try:
    from nlp.learning_assistant import analyze_sentence
except ImportError as error:
    logger.warning("nlp.learning_assistant could not be imported: %s", error)
    analyze_sentence = None

# ============================================================
# GEMINI CONFIGURATION
# ============================================================

# Model: gemini-2.0-flash — free tier: 15 RPM, 1 500 req/day, 1M tokens/day
# Fallback:  gemini-1.5-flash — free tier: 15 RPM, 1 500 req/day
GEMINI_PRIMARY_MODEL   = "gemini-2.0-flash"
GEMINI_FALLBACK_MODEL  = "gemini-1.5-flash"
ACTIVE_MODEL           = GEMINI_PRIMARY_MODEL   # updated at startup if needed
PROVIDER               = "google_gemini"

def get_gemini_key() -> Optional[str]:
    """Retrieve Gemini API key from environment variables."""
    key = (
        os.getenv("GEMINI_API_KEY") or
        os.getenv("GOOGLE_API_KEY") or
        os.getenv("GOOGLE_GEMINI_KEY")
    )
    return key.strip() if key else None


def init_gemini() -> Optional[object]:
    """
    Configure the google-generativeai SDK and return a GenerativeModel instance.
    Returns None and logs a warning if the key is absent or SDK is missing.
    """
    if not GENAI_AVAILABLE:
        logger.error("google-generativeai package is not installed.")
        return None

    key = get_gemini_key()
    if not key:
        logger.warning(
            "GEMINI_API_KEY is not set. AI chat will be unavailable until the key "
            "is configured in the backend environment variables."
        )
        return None

    genai.configure(api_key=key)

    # Try primary model, fall back gracefully
    global ACTIVE_MODEL
    for model_name in (GEMINI_PRIMARY_MODEL, GEMINI_FALLBACK_MODEL):
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 300,
                    "top_p": 0.9,
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                ]
            )
            ACTIVE_MODEL = model_name
            logger.info("Gemini model initialised: %s", model_name)
            return model
        except Exception as err:
            logger.warning("Could not initialise model %s: %s", model_name, err)

    logger.error("All Gemini models failed to initialise.")
    return None


# Initialise once at import time
_gemini_model = init_gemini()


def get_gemini_model():
    """Return the cached Gemini model, or reinitialise if it was never created."""
    global _gemini_model
    if _gemini_model is None:
        _gemini_model = init_gemini()
    return _gemini_model

# ============================================================
# FASTAPI APP & CORS
# ============================================================

app = FastAPI(
    title="SpeakWise AI",
    description="AI English Communication Learning Platform — powered by Google Gemini",
    version="2.0.0"
)

ORIGINS = [
    "https://speak-wise-ai-five.vercel.app",
    "https://speakwise-ai-1.onrender.com",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REQUEST MODELS
# ============================================================

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    language: str = "auto"
    history: List[ChatMessage] = Field(default_factory=list)

class AnalyzeRequest(BaseModel):
    sentence: str

# ============================================================
# LANGUAGE DETECTION
# ============================================================

HINDI_WORDS = {
    "main", "mein", "mujhe", "mujhse", "mujhko",
    "mera", "meri", "mere",
    "aap", "aapko", "aapka", "aapki",
    "tum", "tumhe", "tumko", "tumhara", "tumhari",
    "kya", "kaise", "kaisa", "kaisi",
    "kyun", "kyu", "kyon",
    "hai", "hain", "ho", "haan",
    "nahi", "nahin", "na",
    "kar", "karo", "karna", "karni", "karne",
    "karta", "karti", "karte",
    "raha", "rahi", "rahe",
    "gaya", "gayi", "gaye",
    "jana", "jaana", "jao",
    "aana", "aao", "aata", "aati",
    "acha", "accha", "achha",
    "bahut", "bohot",
    "aaj", "kal", "abhi",
    "baat", "bolo", "bol",
    "suno", "sun", "samajh",
    "chahiye", "pata", "lagta",
    "sakta", "sakti", "sakte",
    "aur", "lekin", "kyunki",
    "ghar", "college",
    "khana", "peena", "hogaya", "hua",
    "kahan", "kab",
    "yaar", "yar",
    "theek", "thik",
    "hum", "ham", "hamara", "humara",
    "apna", "apni",
    "ka", "ki", "ke", "ko", "se", "par",
    "wala", "wali", "wale"
}

def detect_language(text: str) -> str:
    if not text:
        return "english"
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"
    lower_text = text.lower().strip()
    words = re.findall(r"[a-zA-Z]+", lower_text)
    if not words:
        return "english"
    hindi_count = sum(1 for w in words if w in HINDI_WORDS)
    if hindi_count >= 2:
        return "hinglish"
    if hindi_count == 1 and (
        len(words) >= 2 or words[0] in {"kya", "kaise", "haan", "nahi", "khana", "mujhe"}
    ):
        return "hinglish"
    return "english"

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """You are SpeakWise AI, a friendly and encouraging AI conversation partner dedicated to helping people practice English speaking and communication.

Key Guidelines:
1. Natural Conversation: Keep replies concise (2–3 sentences). Be warm, supportive, and motivating.
2. Follow-up Question: Always end with ONE natural follow-up question to keep the conversation active.
3. Language Support:
   - English input → reply in clear, simple English.
   - Hindi input (Devanagari or Hinglish/Roman Hindi) → reply naturally in Hinglish so the user feels comfortable, while gently weaving in English phrases to encourage learning.
   - If the user asks to practice English specifically, switch to simple English.
4. Gentle English Coaching:
   - If the user makes a grammatical error in English, gently note the correct form (e.g., "Quick tip: 'I went to college today' 😊") and continue smoothly.
   - Do NOT give long grammar lectures unless specifically asked.
5. Tone: Warm, positive, and encouraging."""


def build_gemini_prompt(user_message: str, user_language: str, history: List[ChatMessage]) -> str:
    """
    Build a single text prompt for Gemini (non-chat-session mode) that includes
    system instructions, recent conversation history, and the current user message.
    """
    # Language-specific instruction
    if user_language == "hindi":
        lang_note = "The user is writing in Hindi. Reply in friendly, natural Hindi."
    elif user_language == "hinglish":
        lang_note = "The user is writing in Hinglish (Roman Hindi). Reply naturally in Hinglish and encourage English practice."
    else:
        lang_note = "The user is writing in English. Reply in clear, simple English."

    parts = [
        SYSTEM_PROMPT,
        f"\nLanguage context: {lang_note}\n",
    ]

    # Include up to last 8 conversation turns
    if history:
        parts.append("Recent conversation:")
        for msg in history[-8:]:
            role = msg.role.lower().strip()
            content = msg.content.strip()
            if role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"SpeakWise AI: {content}")

    parts.append(f"\nUser: {user_message}")
    parts.append("SpeakWise AI:")

    return "\n".join(parts)

# ============================================================
# ROOT & STATIC ASSETS
# ============================================================

FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

@app.get("/")
def home(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept and os.path.isdir(FRONTEND_DIR):
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
    return {
        "status": "online",
        "name": "SpeakWise AI",
        "version": "2.0.0",
        "message": "SpeakWise backend is running.",
        "model": ACTIVE_MODEL,
        "provider": PROVIDER,
    }

@app.get("/api")
def api_root():
    return {
        "status": "online",
        "name": "SpeakWise AI",
        "version": "2.0.0",
        "message": "SpeakWise backend is running.",
    }

@app.get("/{filename}.{ext}")
def serve_static_assets(filename: str, ext: str):
    file_name = f"{filename}.{ext}"
    if os.path.isdir(FRONTEND_DIR):
        target = os.path.join(FRONTEND_DIR, file_name)
        if os.path.isfile(target):
            return FileResponse(target)
    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": f"{file_name} not found"}
    )

# ============================================================
# HEALTH ENDPOINTS
# ============================================================

@app.get("/health")
@app.get("/api/health")
def health():
    key_present = get_gemini_key() is not None
    sdk_present = GENAI_AVAILABLE
    return {
        "status": "healthy",
        "gemini_key_configured": key_present,
        "gemini_sdk_installed": sdk_present,
        "model": ACTIVE_MODEL,
        "provider": PROVIDER,
        "free_tier_limits": {
            "requests_per_minute": 15,
            "requests_per_day": 1500,
            "tokens_per_day": "1 million",
        },
    }

# ============================================================
# ANALYZE ENDPOINTS
# ============================================================

@app.post("/analyze")
@app.post("/api/analyze")
def analyze_api(request: AnalyzeRequest):
    sentence = (request.sentence or "").strip()
    if not sentence:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error_type": "empty_input",
                "message": "Please enter a sentence to analyze.",
            }
        )

    if analyze is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "service_unavailable",
                "message": "Learning analysis engine is currently unavailable.",
            }
        )

    try:
        result = analyze(sentence)
        return result
    except Exception as error:
        logger.error("Analyze error: %s", error)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_type": "analysis_error",
                "message": "Sentence analysis failed.",
                "error": str(error),
            }
        )

# ============================================================
# CHAT ENDPOINTS
# ============================================================

@app.post("/chat")
@app.post("/api/chat")
def chat(request: ChatRequest):
    message = (request.message or "").strip()
    if not message:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error_type": "empty_message",
                "message": "Please enter a message.",
            }
        )

    # ── Preflight checks ──────────────────────────────────────
    if not GENAI_AVAILABLE:
        logger.error("google-generativeai package is not installed on the server.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_type": "dependency_error",
                "message": (
                    "The google-generativeai Python package is not installed on the backend. "
                    "Add 'google-generativeai>=0.8.0' to requirements.txt and redeploy."
                ),
                "provider": PROVIDER,
            }
        )

    if not get_gemini_key():
        logger.warning("Chat request rejected: GEMINI_API_KEY not configured.")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "missing_configuration",
                "message": (
                    "GEMINI_API_KEY is not set on the backend. "
                    "Add it as an environment variable on Render (Dashboard → Environment) "
                    "and redeploy the service. Get a free key at https://aistudio.google.com."
                ),
                "provider": PROVIDER,
            }
        )

    # ── Language detection ────────────────────────────────────
    requested_language = request.language.strip().lower()
    detected_language  = detect_language(message)
    user_language = (
        requested_language if requested_language in {"hindi", "hinglish", "english"}
        else detected_language
    )

    # ── Optional learning analysis ────────────────────────────
    learning = {}
    if analyze_sentence is not None:
        try:
            learning = analyze_sentence(message)
        except Exception as err:
            logger.debug("analyze_sentence error: %s", err)

    # ── Build prompt ──────────────────────────────────────────
    prompt = build_gemini_prompt(
        user_message=message,
        user_language=user_language,
        history=request.history,
    )

    # ── Call Gemini API ───────────────────────────────────────
    model = get_gemini_model()
    if model is None:
        logger.error("Gemini model is not available despite key being set.")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "model_init_error",
                "message": "Gemini model could not be initialised. Check server logs.",
                "provider": PROVIDER,
            }
        )

    try:
        gemini_response = model.generate_content(prompt)

        # Extract text safely
        answer = ""
        try:
            answer = gemini_response.text.strip()
        except Exception:
            # Fallback: iterate parts
            for part in (gemini_response.parts or []):
                if hasattr(part, "text") and part.text:
                    answer += part.text

        answer = answer.strip()

        if not answer:
            # Check for safety blocks
            block_reason = None
            try:
                block_reason = str(gemini_response.prompt_feedback)
            except Exception:
                pass
            logger.warning("Gemini returned empty response. Feedback: %s", block_reason)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "success": False,
                    "error_type": "empty_response",
                    "message": "The AI returned an empty response. This may be due to safety filters. Please rephrase your message.",
                    "provider": PROVIDER,
                }
            )

        ai_language = detect_language(answer)

        return {
            "success": True,
            "message": message,
            "response": answer,
            "language": ai_language,
            "user_language": user_language,
            "model": ACTIVE_MODEL,
            "provider": PROVIDER,
            "learning": learning,
        }

    except Exception as err:
        err_str = str(err)

        # Never leak the API key in error messages
        api_key = get_gemini_key()
        if api_key and api_key in err_str:
            err_str = err_str.replace(api_key, "[REDACTED]")

        logger.error("Gemini API error: %s", err_str)

        # Quota exhausted (HTTP 429 / RESOURCE_EXHAUSTED)
        if any(kw in err_str.lower() for kw in ("429", "quota", "resource_exhausted", "rate limit")):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error_type": "quota_exceeded",
                    "message": (
                        "Google Gemini free-tier quota reached (15 requests/min or 1 500 req/day). "
                        "Please wait a moment and try again. "
                        "Free limits reset every minute (RPM) and every day at midnight Pacific time."
                    ),
                    "provider": PROVIDER,
                    "model": ACTIVE_MODEL,
                }
            )

        # Invalid API key / permission denied
        if any(kw in err_str.lower() for kw in ("401", "403", "api_key", "invalid", "permission", "unauthenticated")):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error_type": "authentication_error",
                    "message": (
                        "GEMINI_API_KEY is invalid or has been revoked. "
                        "Generate a new key at https://aistudio.google.com/apikey and update "
                        "the environment variable on Render."
                    ),
                    "provider": PROVIDER,
                }
            )

        # Model not found / deprecated
        if any(kw in err_str.lower() for kw in ("404", "not found", "model")):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "success": False,
                    "error_type": "model_unavailable",
                    "message": f"Gemini model '{ACTIVE_MODEL}' is not available. Check Google AI Studio for current model names.",
                    "provider": PROVIDER,
                }
            )

        # Timeout
        if any(kw in err_str.lower() for kw in ("timeout", "timed out", "deadline")):
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "success": False,
                    "error_type": "timeout",
                    "message": "The Gemini API request timed out. Please try again.",
                    "provider": PROVIDER,
                }
            )

        # Generic error — surface a sanitised message, no fake responses
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "provider_error",
                "message": f"Gemini API error: {err_str[:200]}",
                "provider": PROVIDER,
            }
        )

# ============================================================
# SERVER STARTUP LOG
# ============================================================

logger.info(
    "SpeakWise AI Backend v2.0 initialised — provider: %s, model: %s, sdk: %s",
    PROVIDER, ACTIVE_MODEL, GENAI_AVAILABLE
)