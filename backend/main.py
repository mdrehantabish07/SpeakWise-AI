import os
import sys
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from huggingface_hub import InferenceClient


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ROOT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# ============================================================
# SPEAKWISE ENGINE
# ============================================================

try:
    from speakwise_engine import analyze

except ImportError as error:

    print(
        "WARNING: speakwise_engine could not be imported:"
    )

    print(error)

    analyze = None


# ============================================================
# LEARNING ASSISTANT
# ============================================================

try:
    from nlp.learning_assistant import analyze_sentence

except ImportError as error:

    print(
        "WARNING: learning_assistant could not be imported:"
    )

    print(error)

    analyze_sentence = None


# ============================================================
# HUGGING FACE CONFIGURATION
# ============================================================

MODEL_NAMES = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
]

MODEL_NAME = MODEL_NAMES[0]

# IMPORTANT:
# Read Hugging Face token from environment variable.
# Never hard-code the token in this file.

HF_TOKEN = os.getenv("HF_TOKEN")


# ============================================================
# FASTAPI APP & CORS
# ============================================================

app = FastAPI(
    title="SpeakWise AI",
    description="AI English Communication Learning Platform",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    history: list[ChatMessage] = Field(
        default_factory=list
    )


class AnalyzeRequest(BaseModel):

    sentence: str


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text: str) -> str:

    if not text:
        return "english"


    # --------------------------------------------------------
    # Hindi Devanagari
    # --------------------------------------------------------

    if re.search(
        r"[\u0900-\u097F]",
        text
    ):

        return "hindi"


    lower_text = (
        text
        .lower()
        .strip()
    )


    # --------------------------------------------------------
    # Common Roman Hindi words
    # --------------------------------------------------------

    hindi_words = {

        "main",
        "mein",
        "mujhe",
        "mujhse",
        "mujhko",

        "mera",
        "meri",
        "mere",

        "aap",
        "aapko",
        "aapka",
        "aapki",

        "tum",
        "tumhe",
        "tumko",
        "tumhara",
        "tumhari",

        "kya",
        "kaise",
        "kaisa",
        "kaisi",

        "kyun",
        "kyu",
        "kyon",

        "hai",
        "hain",
        "ho",
        "haan",

        "nahi",
        "nahin",

        "kar",
        "karo",
        "karna",
        "karni",
        "karne",

        "karta",
        "karti",
        "karte",

        "raha",
        "rahi",
        "rahe",

        "gaya",
        "gayi",
        "gaye",

        "jana",
        "jaana",
        "jao",

        "aana",
        "aao",

        "acha",
        "accha",
        "achha",

        "bahut",
        "bohot",

        "aaj",
        "kal",
        "abhi",

        "baat",
        "bolo",
        "bol",

        "suno",
        "sun",

        "samajh",

        "chahiye",

        "pata",
        "lagta",

        "sakta",
        "sakti",
        "sakte",

        "aur",
        "lekin",
        "kyunki",

        "ghar",
        "college",

        "khana",
        "peena",

        "kahan",
        "kab",

        "yaar",
        "yar",

        "theek",
        "thik",

        "hum",
        "ham",

        "hamara",
        "humara",

        "apna",
        "apni",

        "ka",
        "ki",
        "ke",

        "ko",
        "se",
        "par",

        "wala",
        "wali",
        "wale"

    }


    words = re.findall(
        r"[a-zA-Z]+",
        lower_text
    )


    if not words:
        return "english"


    hindi_count = sum(
        1
        for word in words
        if word in hindi_words
    )


    # --------------------------------------------------------
    # Determine Roman Hindi / Hinglish
    # --------------------------------------------------------

    if hindi_count >= 2:
        return "hinglish"


    if hindi_count == 1:

        if len(words) >= 3:
            return "hinglish"


    return "english"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are SpeakWise AI.

You are a friendly AI conversation partner
for people who want to improve English communication.

Your MAIN PURPOSE is conversation practice.

The user may speak:

1. English
2. Hindi
3. Hinglish
4. Roman Hindi
5. Mixed Hindi and English

IMPORTANT:

Understand what the user means before replying.

Do NOT simply repeat what the user said.

Do NOT translate every sentence.

Do NOT behave like a textbook.

Do NOT give long grammar lectures.

The conversation should feel like a REAL FRIENDLY
conversation between two people.

==================================================
LANGUAGE BEHAVIOR
==================================================

If the user speaks English:

Reply in simple, natural English.

If the user speaks Hindi:

Reply naturally in Hindi.

If the user speaks Hinglish:

Reply naturally in Hinglish.

Hinglish means Hindi and English can naturally
appear together in the same sentence.

Example:

User:
mujhe english improve karni hai

Good response:
Bilkul! Hum daily thodi-thodi English conversation
practice kar sakte hain. Aaj se start karte hain 😊
What did you do today?

Another example:

User:
aaj mera college tha and I was very tired

Good response:
Ohh, samajh sakta hoon 😄 College ke baad tired
feel hona normal hai. What did you do in college today?

==================================================
VERY IMPORTANT
==================================================

If the user asks:

"mujhse hinglish me baat karo"

Then continue speaking in Hinglish.

If the user asks:

"mujhse hindi me baat karo"

Then continue speaking in Hindi.

If the user asks:

"talk to me in English"

Then continue in simple English.

Remember the requested language during the conversation.

==================================================
ENGLISH LEARNING
==================================================

The goal is communication practice.

If the user makes an important English mistake,
correct it gently.

Use this short format only when useful:

Better sentence:
"I went to college today."

Then continue the conversation.

Do not correct every tiny mistake.

Do not interrupt natural conversation with
too many corrections.

==================================================
CONVERSATION
==================================================

Keep the conversation alive.

After answering the user, ask ONE natural
follow-up question whenever appropriate.

Do not end the conversation with:

"Your turn."

Do not say:

"Now it is your turn."

Do not repeatedly say:

"How can I help you?"

Instead, continue naturally.

Example:

User:
I went to college today.

Assistant:
Nice! How was your college today?
Did you have any interesting classes?

User:
haan ek AI ka lecture tha

Assistant:
Oh nice! AI is really interesting 😄
What did you learn in that lecture?

==================================================
STYLE
==================================================

Be:

friendly
natural
short
encouraging
easy to understand

Use simple English when English is being practiced.

Use natural Hindi/Hinglish when the user uses Hindi/Hinglish.

Do not mention these instructions.

Do not talk about being an AI unless the user asks.

Never output programming instructions unless the user
specifically asks about programming.
"""


# ============================================================
# BUILD CONVERSATION MESSAGES
# ============================================================

def build_messages(
    user_message: str,
    user_language: str,
    history: list[ChatMessage]
):

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }

    ]


    # --------------------------------------------------------
    # Language instruction
    # --------------------------------------------------------

    if user_language == "hindi":

        language_instruction = """
The user's current language is Hindi.

Reply naturally in Hindi.
Do not translate the Hindi message into English.
"""

    elif user_language == "hinglish":

        language_instruction = """
The user's current language is Hinglish / Roman Hindi.

Reply naturally in Hinglish.
Use Hindi + English naturally.
Do NOT convert the user's Hinglish into pure English.
"""

    elif user_language == "english":

        language_instruction = """
The user's current language is English.

Reply in simple natural English.
"""

    else:

        language_instruction = """
Detect the user's language from the conversation
and reply naturally in the same language style.
"""


    messages.append(
        {
            "role": "system",
            "content": language_instruction
        }
    )


    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    for item in history[-10:]:

        role = item.role

        content = item.content.strip()


        if role not in {
            "user",
            "assistant"
        }:

            continue


        if not content:
            continue


        messages.append(
            {
                "role": role,
                "content": content
            }
        )


    # --------------------------------------------------------
    # Current user message
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    return messages


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():

    return {

        "status": "online",

        "name": "SpeakWise AI",

        "version": "1.0.0",

        "message":
            "SpeakWise backend is running."

    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "huggingface_configured":
            HF_TOKEN is not None,

        "model":
            MODEL_NAME

    }


# ============================================================
# ANALYZE
# ============================================================

@app.post("/analyze")
def analyze_api(
    request: AnalyzeRequest
):

    sentence = request.sentence.strip()


    if not sentence:

        return {

            "success": False,

            "message":
                "Please enter a sentence."

        }


    # --------------------------------------------------------
    # SpeakWise Engine
    # --------------------------------------------------------

    if analyze is None:

        return {

            "success": False,

            "message":
                "SpeakWise engine is not available."

        }


    try:

        result = analyze(sentence)

        return result


    except Exception as error:

        return {

            "success": False,

            "message":
                "Sentence analysis failed.",

            "error":
                str(error)

        }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest
):

    message = request.message.strip()


    if not message:

        return {

            "success": False,

            "message":
                "Please enter a message."

        }


    # ========================================================
    # DETECT LANGUAGE
    # ========================================================

    requested_language = (
        request.language
        .strip()
        .lower()
    )


    detected_language = detect_language(
        message
    )


    # --------------------------------------------------------
    # Respect valid frontend language
    # --------------------------------------------------------

    if requested_language in {
        "hindi",
        "hinglish",
        "english"
    }:

        user_language = requested_language

    else:

        user_language = detected_language


    print(
        "User:",
        message
    )

    print(
        "Detected language:",
        user_language
    )


    # ========================================================
    # GET HF CLIENT
    # ========================================================

    hf_token = os.getenv("HF_TOKEN")

    client = None


    if hf_token:

        try:

            client = InferenceClient(
                api_key=hf_token
            )

        except Exception as err:

            print(
                "HF client error:",
                err
            )


    # ========================================================
    # LEARNING ANALYSIS
    # ========================================================

    learning = {}


    if analyze_sentence is not None:

        try:

            learning = analyze_sentence(
                message
            )

        except Exception as error:

            print(
                "Learning analysis error:",
                error
            )

            learning = {}


    # ========================================================
    # AI ANSWER
    # ========================================================

    answer = ""


    if client is not None:

        messages = build_messages(
            user_message=message,
            user_language=user_language,
            history=request.history
        )


        for model in MODEL_NAMES:

            try:

                response = client.chat_completion(
                    model=model,
                    messages=messages,
                    max_tokens=220,
                    temperature=0.7
                )


                if (
                    response
                    and response.choices
                    and response.choices[0].message
                ):

                    answer = (
                        response
                        .choices[0]
                        .message
                        .content
                        or ""
                    )


                    if answer.strip():
                        break


            except Exception as err:

                print(
                    f"Error with model {model}:",
                    err
                )


    # ========================================================
    # SMART FALLBACK
    # ========================================================

    if not answer.strip():

        if user_language in [
            "hindi",
            "hinglish"
        ]:

            answer = (
                "Bahut badiya! Maine aapki baat samajh li. "
                "SpeakWise AI is listening. "
                "Let's practice English together — "
                "try telling me more in English!"
            )

        else:

            answer = (
                "Great effort! I heard you clearly. "
                "Let's keep practicing your English speaking. "
                "What would you like to talk about next?"
            )


    # ========================================================
    # AI LANGUAGE
    # ========================================================

    ai_language = detect_language(
        answer
    )


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "success": True,

        "message": message,

        "response": answer,

        "language": ai_language,

        "user_language": user_language,

        "learning": learning

    }


# ============================================================
# SERVER INFORMATION
# ============================================================

print()

print(
    "=========================================="
)

print(
    "             SPEAKWISE AI"
)

print(
    "             FASTAPI BACKEND"
)

print(
    "=========================================="
)

print()

print(
    "Backend ready."
)

print()

print(
    "Model:",
    MODEL_NAME
)

print(
    "HuggingFace:",
    "Configured"
    if HF_TOKEN
    else
    "NOT CONFIGURED"
)

print()

print(
    "Available endpoints:"
)

print(
    "GET  /"
)

print(
    "GET  /health"
)

print(
    "POST /analyze"
)

print(
    "POST /chat"
)

print()