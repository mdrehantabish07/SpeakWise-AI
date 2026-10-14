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

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Configure logging (Never log tokens or credentials)
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
# HUGGING FACE ROUTER CONFIGURATION
# ============================================================

MODEL_NAME = "CohereLabs/aya-expanse-32b:cohere"
HF_ROUTER_BASE_URL = "https://router.huggingface.co/v1"

def get_hf_token() -> Optional[str]:
    """Retrieve Hugging Face token from environment variables."""
    token = (
        os.getenv("HF_TOKEN") or
        os.getenv("HUGGINGFACE_API_KEY") or
        os.getenv("HUGGINGFACEHUB_API_TOKEN") or
        os.getenv("HF_API_KEY")
    )
    if token:
        token = token.strip()
    return token or None

def create_ai_client() -> OpenAI:
    """Create OpenAI-compatible client pointing to Hugging Face router."""
    token = get_hf_token()
    if not token:
        raise RuntimeError("HF_TOKEN is not configured on the backend.")
    if OpenAI is None:
        raise RuntimeError("openai Python SDK is not installed.")
    return OpenAI(
        base_url=HF_ROUTER_BASE_URL,
        api_key=token,
        timeout=25.0
    )

# ============================================================
# FASTAPI APP & CORS
# ============================================================

app = FastAPI(
    title="SpeakWise AI",
    description="AI English Communication Learning Platform",
    version="1.0.0"
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

    # Hindi Devanagari script check
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    lower_text = text.lower().strip()
    words = re.findall(r"[a-zA-Z]+", lower_text)
    if not words:
        return "english"

    hindi_count = sum(1 for word in words if word in HINDI_WORDS)

    if hindi_count >= 2:
        return "hinglish"
    if hindi_count == 1 and (len(words) >= 2 or words[0] in {"kya", "kaise", "haan", "nahi", "khana", "mujhe"}):
        return "hinglish"

    return "english"

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """You are SpeakWise AI, a friendly and encouraging AI conversation partner dedicated to helping people practice English speaking and communication.

Key Guidelines:
1. Natural Conversation: Treat every interaction like a friendly, supportive conversation. Keep replies concise (typically 2 to 3 sentences).
2. Follow-up Question: Always keep the conversation active by asking ONE natural, engaging follow-up question.
3. Language Support:
   - If the user writes in English, reply in clear, friendly English.
   - If the user writes in Hindi or Hinglish (Roman Hindi), reply naturally in Hinglish/Hindi so they feel understood, while gently weaving in simple English phrases to encourage their learning.
   - If the user specifically asks to practice in English, use simple English.
4. Gentle English Learning:
   - When the user makes an English grammatical mistake, gently acknowledge the correct way (e.g. "Better: 'I went to college today' 😊") and continue the conversation smoothly.
   - Do NOT lecture or give long grammar lessons unless specifically asked.
5. Tone: Warm, positive, supportive, and motivating."""

def build_messages(user_message: str, user_language: str, history: List[ChatMessage]) -> list:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Language instruction
    if user_language == "hindi":
        messages.append({
            "role": "system",
            "content": "The user is communicating in Hindi. Reply in friendly, natural Hindi."
        })
    elif user_language == "hinglish":
        messages.append({
            "role": "system",
            "content": "The user is communicating in Hinglish (Roman Hindi). Reply naturally in Hinglish and encourage English practice."
        })
    elif user_language == "english":
        messages.append({
            "role": "system",
            "content": "The user is communicating in English. Reply in clear, simple English and encourage their practice."
        })

    # Recent history turns (up to 10)
    for item in history[-10:]:
        role = item.role.lower().strip()
        content = item.content.strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    # Current user message
    messages.append({"role": "user", "content": user_message})
    return messages

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
        "version": "1.0.0",
        "message": "SpeakWise backend is running.",
        "model": MODEL_NAME
    }

@app.get("/api")
def api_root():
    return {
        "status": "online",
        "name": "SpeakWise AI",
        "version": "1.0.0",
        "message": "SpeakWise backend is running."
    }

@app.get("/{filename}.{ext}")
def serve_static_assets(filename: str, ext: str):
    file_name = f"{filename}.{ext}"
    if os.path.isdir(FRONTEND_DIR):
        target = os.path.join(FRONTEND_DIR, file_name)
        if os.path.isfile(target):
            return FileResponse(target)
    return JSONResponse(status_code=404, content={"status": "error", "message": f"{file_name} not found"})

# ============================================================
# HEALTH ENDPOINTS
# ============================================================

@app.get("/health")
@app.get("/api/health")
def health():
    token = get_hf_token()
    return {
        "status": "healthy",
        "huggingface_configured": token is not None,
        "model": MODEL_NAME,
        "provider": "huggingface_router"
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
                "message": "Please enter a sentence to analyze."
            }
        )

    if analyze is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "service_unavailable",
                "message": "Learning analysis engine is currently unavailable."
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
                "error": str(error)
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
                "message": "Please enter a message."
            }
        )

    hf_token = get_hf_token()
    if not hf_token:
        logger.warning("Chat request failed: HF_TOKEN is not configured.")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "missing_configuration",
                "status_code": 503,
                "message": "HF_TOKEN is not configured on the backend. Please configure your Hugging Face API token in environment variables.",
                "provider": "huggingface"
            }
        )

    if OpenAI is None:
        logger.error("Chat request failed: openai package is not installed.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_type": "dependency_error",
                "status_code": 500,
                "message": "The official 'openai' Python SDK is not installed on the backend server.",
                "provider": "huggingface"
            }
        )

    # Determine user language
    requested_language = request.language.strip().lower()
    detected_language = detect_language(message)
    if requested_language in {"hindi", "hinglish", "english"}:
        user_language = requested_language
    else:
        user_language = detected_language

    # Run optional learning analysis on input
    learning = {}
    if analyze_sentence is not None:
        try:
            learning = analyze_sentence(message)
        except Exception as error:
            logger.debug("Sentence analysis during chat error: %s", error)
            learning = {}

    # Build prompt messages
    messages = build_messages(
        user_message=message,
        user_language=user_language,
        history=request.history
    )

    # Create client
    try:
        client = create_ai_client()
    except Exception as err:
        logger.error("Failed to create AI client: %s", err)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_type": "client_initialization_error",
                "message": str(err),
                "provider": "huggingface"
            }
        )

    # Attempt AI chat completion
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=250,
            temperature=0.7
        )

        if not response or not response.choices or not response.choices[0].message:
            raise RuntimeError("Received empty choices from Hugging Face router.")

        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            raise RuntimeError("Model returned empty response content.")

        ai_language = detect_language(answer)

        return {
            "success": True,
            "message": message,
            "response": answer,
            "language": ai_language,
            "user_language": user_language,
            "model": MODEL_NAME,
            "learning": learning
        }

    except Exception as err:
        # Extract status code and sanitize error message (Never leak tokens)
        err_status = getattr(err, "status_code", None)
        err_str = str(err)
        if hf_token and hf_token in err_str:
            err_str = err_str.replace(hf_token, "[REDACTED_TOKEN]")

        logger.error("Hugging Face API request failed (status=%s): %s", err_status, err_str)

        # 402: Insufficient credits on Hugging Face account
        if err_status == 402 or "credits" in err_str.lower():
            return JSONResponse(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                content={
                    "success": False,
                    "error_type": "insufficient_credits",
                    "status_code": 402,
                    "model": MODEL_NAME,
                    "provider": "huggingface",
                    "message": "Hugging Face account inference credits exhausted (HTTP 402). Purchase pre-paid credits or subscribe to PRO on Hugging Face to enable live AI responses.",
                    "action_required": "Please add credits at https://huggingface.co/settings/billing or upgrade to PRO."
                }
            )

        # 401: Invalid token
        if err_status == 401 or "unauthorized" in err_str.lower():
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error_type": "authentication_error",
                    "status_code": 401,
                    "model": MODEL_NAME,
                    "provider": "huggingface",
                    "message": "Invalid Hugging Face API token. Please verify your HF_TOKEN configuration."
                }
            )

        # 429: Rate limited
        if err_status == 429 or "rate limit" in err_str.lower():
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error_type": "rate_limited",
                    "status_code": 429,
                    "model": MODEL_NAME,
                    "provider": "huggingface",
                    "message": "Hugging Face rate limit reached. Please wait a moment and try again."
                }
            )

        # 400: Model not supported / bad request
        if err_status == 400 or "not supported" in err_str.lower():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error_type": "model_unavailable",
                    "status_code": 400,
                    "model": MODEL_NAME,
                    "provider": "huggingface",
                    "message": f"Requested AI model '{MODEL_NAME}' is currently unavailable on Hugging Face router."
                }
            )

        # Timeout
        if "timeout" in err_str.lower() or "timed out" in err_str.lower():
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "success": False,
                    "error_type": "timeout",
                    "status_code": 504,
                    "model": MODEL_NAME,
                    "provider": "huggingface",
                    "message": "AI model request timed out. Please try sending your message again."
                }
            )

        # Generic provider error
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error_type": "provider_error",
                "status_code": 503,
                "model": MODEL_NAME,
                "provider": "huggingface",
                "message": "Hugging Face inference service error. Please try again in a few moments."
            }
        )

# ============================================================
# SERVER STARTUP LOG
# ============================================================

logger.info("SpeakWise AI Backend initialized with model: %s", MODEL_NAME)