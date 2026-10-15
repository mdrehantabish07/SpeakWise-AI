
import os
import sys
import re
import logging
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False


# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("speakwise.backend")


# ------------------------------------------------------------
# PATHS AND ENVIRONMENT
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

PROVIDER = "groq"
ACTIVE_MODEL = "openai/gpt-oss-20b"


# ------------------------------------------------------------
# OPTIONAL SPEAKWISE MODULES
# ------------------------------------------------------------

try:
    from speakwise_engine import analyze
except ImportError as error:
    logger.warning("speakwise_engine unavailable: %s", error)
    analyze = None

try:
    from nlp.learning_assistant import analyze_sentence
except ImportError as error:
    logger.warning("Learning assistant unavailable: %s", error)
    analyze_sentence = None


# ------------------------------------------------------------
# GROQ CLIENT
# ------------------------------------------------------------

def get_groq_key() -> Optional[str]:
    key = os.getenv("GROQ_API_KEY")
    return key.strip() if key else None


def init_groq():
    if not GROQ_AVAILABLE:
        logger.error("Groq SDK is not installed.")
        return None

    key = get_groq_key()
    if not key:
        logger.warning("GROQ_API_KEY is not configured.")
        return None

    try:
        client = Groq(api_key=key)
        logger.info("Groq client initialized.")
        return client
    except Exception:
        logger.exception("Could not initialize Groq client.")
        return None


_groq_client = init_groq()


def get_groq_client():
    global _groq_client

    if _groq_client is None:
        _groq_client = init_groq()

    return _groq_client


# ------------------------------------------------------------
# FASTAPI AND CORS
# ------------------------------------------------------------

app = FastAPI(
    title="SpeakWise AI",
    description="AI English Communication Learning Platform powered by Groq",
    version="3.0.0",
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


# ------------------------------------------------------------
# REQUEST MODELS
# ------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    language: str = "auto"
    history: List[ChatMessage] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    sentence: str


# ------------------------------------------------------------
# LANGUAGE DETECTION
# ------------------------------------------------------------

HINDI_WORDS = {
    "main", "mein", "mujhe", "mujhse", "mujhko",
    "mera", "meri", "mere", "aap", "aapko", "aapka",
    "aapki", "tum", "tumhe", "tumko", "tumhara",
    "tumhari", "kya", "kaise", "kaisa", "kaisi",
    "kyun", "kyu", "kyon", "hai", "hain", "ho", "haan",
    "nahi", "nahin", "na", "kar", "karo", "karna",
    "karni", "karne", "karta", "karti", "karte",
    "raha", "rahi", "rahe", "gaya", "gayi", "gaye",
    "jana", "jaana", "jao", "aana", "aao", "aata",
    "aati", "acha", "accha", "achha", "bahut", "bohot",
    "aaj", "kal", "abhi", "baat", "bolo", "bol",
    "suno", "samajh", "chahiye", "pata", "lagta",
    "sakta", "sakti", "sakte", "aur", "lekin", "kyunki",
    "ghar", "college", "khana", "peena", "hogaya", "hua",
    "kahan", "kab", "yaar", "yar", "theek", "thik",
    "hum", "ham", "hamara", "humara", "apna", "apni",
    "ka", "ki", "ke", "ko", "se", "par",
    "wala", "wali", "wale",
}


def detect_language(text: str) -> str:
    if not text:
        return "english"

    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    words = re.findall(r"[a-zA-Z]+", text.lower())

    if not words:
        return "english"

    hindi_count = sum(1 for word in words if word in HINDI_WORDS)

    if hindi_count >= 2:
        return "hinglish"

    if hindi_count == 1 and (
        len(words) >= 2
        or words[0] in {"kya", "kaise", "haan", "nahi", "khana", "mujhe"}
    ):
        return "hinglish"

    return "english"


# ------------------------------------------------------------
# AI SYSTEM PROMPT
# ------------------------------------------------------------

SYSTEM_PROMPT = """
You are SpeakWise AI, a friendly AI conversation partner helping
people practice English speaking and communication.

Guidelines:
1. Reply naturally and usually in 2-3 sentences.
2. End with one relevant follow-up question when appropriate.
3. English input: reply in simple, clear English.
4. Hinglish input: reply naturally in Roman Hinglish.
5. Hindi written in Devanagari: reply in natural Hindi.
6. If the user requests English practice, use simple English.
7. Correct English mistakes gently and briefly.
8. Be warm, helpful, respectful, and conversational.
9. Answer the user's actual question. Do not use generic fallback
   replies when a meaningful answer is possible.
"""


def build_messages(
    user_message: str,
    user_language: str,
    history: List[ChatMessage],
) -> list:
    if user_language == "hindi":
        language_note = (
            "The user is writing Hindi in Devanagari. "
            "Reply in natural Hindi."
        )
    elif user_language == "hinglish":
        language_note = (
            "The user is writing Roman Hindi/Hinglish. "
            "Reply naturally in Roman Hinglish."
        )
    else:
        language_note = "Reply in simple, clear English."

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n" + language_note,
        }
    ]

    for item in history[-8:]:
        role = item.role.lower().strip()
        content = item.content.strip()

        if role in {"user", "assistant"} and content:
            messages.append({
                "role": role,
                "content": content,
            })

    messages.append({
        "role": "user",
        "content": user_message,
    })

    return messages


# ------------------------------------------------------------
# ROOT AND STATIC ASSETS
# ------------------------------------------------------------

FRONTEND_DIR = ROOT_DIR / "frontend"


@app.get("/")
def home(request: Request):
    index_file = FRONTEND_DIR / "index.html"

    if (
        "text/html" in request.headers.get("accept", "")
        and index_file.is_file()
    ):
        return FileResponse(index_file)

    return {
        "status": "online",
        "name": "SpeakWise AI",
        "version": "3.0.0",
        "message": "SpeakWise backend is running.",
        "model": ACTIVE_MODEL,
        "provider": PROVIDER,
    }


@app.get("/api")
def api_root():
    return {
        "status": "online",
        "name": "SpeakWise AI",
        "version": "3.0.0",
        "provider": PROVIDER,
        "model": ACTIVE_MODEL,
    }


@app.get("/{filename}.{ext}")
def serve_static_assets(filename: str, ext: str):
    file_name = f"{filename}.{ext}"
    target = FRONTEND_DIR / file_name

    if target.is_file():
        return FileResponse(target)

    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": f"{file_name} not found",
        },
    )


# ------------------------------------------------------------
# HEALTH ENDPOINTS
# ------------------------------------------------------------

@app.get("/health")
@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "provider": PROVIDER,
        "model": ACTIVE_MODEL,
        "api_key_configured": bool(get_groq_key()),
        "sdk_installed": GROQ_AVAILABLE,
    }


# ------------------------------------------------------------
# SENTENCE ANALYSIS
# ------------------------------------------------------------

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
            },
        )

    if analyze is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "service_unavailable",
                "message": "Learning analysis engine is unavailable.",
            },
        )

    try:
        return analyze(sentence)
    except Exception:
        logger.exception("Sentence analysis failed.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_type": "analysis_error",
                "message": "Sentence analysis failed.",
            },
        )


# ------------------------------------------------------------
# CHAT ENDPOINTS
# ------------------------------------------------------------

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
            },
        )

    if not GROQ_AVAILABLE:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_type": "dependency_error",
                "message": "Groq SDK is missing. Install it using pip install groq.",
            },
        )

    if not get_groq_key():
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "missing_configuration",
                "message": "GROQ_API_KEY is not configured on the backend.",
            },
        )

    requested_language = (request.language or "auto").strip().lower()
    detected_language = detect_language(message)

    user_language = (
        requested_language
        if requested_language in {"hindi", "hinglish", "english"}
        else detected_language
    )

    learning = {}

    if analyze_sentence is not None:
        try:
            learning = analyze_sentence(message)
        except Exception:
            logger.exception("Optional learning analysis failed.")

    client = get_groq_client()

    if client is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "client_initialization_error",
                "message": "Could not initialize the Groq client.",
            },
        )

    try:
        messages = build_messages(
            user_message=message,
            user_language=user_language,
            history=request.history,
        )

        result = client.chat.completions.create(
            model=ACTIVE_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )

        answer = (
            result.choices[0].message.content
            if result.choices
            else None
        )

        answer = answer.strip() if answer else ""

        if not answer:
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={
                    "success": False,
                    "error_type": "empty_response",
                    "message": "The AI returned an empty response. Please try again.",
                },
            )

        return {
            "success": True,
            "message": message,
            "response": answer,
            "language": detect_language(answer),
            "user_language": user_language,
            "model": ACTIVE_MODEL,
            "provider": PROVIDER,
            "learning": learning,
        }

    except Exception as error:
        error_text = str(error).lower()
        logger.error("Groq API request failed: %s", type(error).__name__)

        if any(term in error_text for term in ("429", "rate_limit", "quota")):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error_type": "quota_exceeded",
                    "message": "Groq usage limit reached. Please try again later or check your Groq Console limits.",
                    "provider": PROVIDER,
                },
            )

        if any(term in error_text for term in ("401", "403", "authentication", "api_key")):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error_type": "authentication_error",
                    "message": "Groq API authentication failed. Check GROQ_API_KEY.",
                    "provider": PROVIDER,
                },
            )

        if any(term in error_text for term in ("404", "model_not_found")):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "success": False,
                    "error_type": "model_unavailable",
                    "message": "The configured Groq model is unavailable.",
                    "provider": PROVIDER,
                    "model": ACTIVE_MODEL,
                },
            )

        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "success": False,
                "error_type": "provider_error",
                "message": "Groq could not complete the request. Check backend logs and try again.",
                "provider": PROVIDER,
            },
        )


# ------------------------------------------------------------
# STARTUP LOG
# ------------------------------------------------------------

logger.info(
    "SpeakWise backend initialized: provider=%s, model=%s, sdk=%s, key_configured=%s",
    PROVIDER,
    ACTIVE_MODEL,
    GROQ_AVAILABLE,
    bool(get_groq_key()),
)
