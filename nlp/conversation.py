import os
import time
from huggingface_hub import InferenceClient


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_NAME = "openai/gpt-oss-20b"

MAX_HISTORY = 20


# ==========================================
# HUGGING FACE TOKEN
# ==========================================

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("❌ HF_TOKEN is not configured.")
    print()
    print('Run in PowerShell:')
    print('$env:HF_TOKEN="YOUR_TOKEN"')
    raise SystemExit


# ==========================================
# CLIENT
# ==========================================

client = InferenceClient(
    api_key=HF_TOKEN,
    provider="auto"
)


# ==========================================
# LANGUAGE STYLE
# ==========================================

language_mode = "auto"


# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are SpeakWise AI.

You are a friendly and natural conversation
partner for an English communication learning
platform.

The user can communicate using:

English
Hindi
Hinglish
Roman Hindi
Mixed Hindi and English
Incorrect English
Short informal messages

Your job is to understand the user's meaning
and have a natural conversation.

==============================================
LANGUAGE BEHAVIOR
==============================================

The current language style is controlled by
the application.

If the style is AUTO:

Detect the language/style from the user's
latest message.

If the user writes English:
reply in English.

If the user writes Hindi:
reply in Hindi.

If the user writes Hinglish:
reply in natural Hinglish.

If the user mixes Hindi and English:
you may naturally mix Hindi and English.

Do NOT translate every message.

Do NOT explain the language mode.

Do NOT say that you are changing languages.

Just communicate naturally.

==============================================
HINGLISH
==============================================

When the user uses Hinglish, use natural
Roman Hindi mixed with English.

Example:

User:
kai kar rahe hai

Assistant:
Main bas aapse baat kar raha hoon! 😄
Aur aap kya kar rahe ho?

Example:

User:
mujhe kal college jana hai

Assistant:
Achha! Aapko kal college jana hai.
Kal college mein kya hai?

Example:

User:
main AI and Data Science padh raha hu

Assistant:
Oh nice! 😄 Aap AI and Data Science
padh rahe ho. Aapko Machine Learning
mein interest hai?

==============================================
ENGLISH
==============================================

If the user speaks English, use simple
natural English.

Example:

User:
hello

Assistant:
Hello! 😊 How are you today?

==============================================
GRAMMAR
==============================================

The user is learning English.

If the user makes an important English
grammar mistake, gently correct it.

Do not correct every small mistake.

Use:

Better sentence:
"I went to college yesterday."

Then continue the conversation.

Example:

User:
I go college yesterday.

Assistant:
Better sentence:
"I went to college yesterday." 😊

What did you do at college?

==============================================
CONVERSATION
==============================================

Remember previous messages.

If the user tells you their name,
remember it.

If the user tells you what they study,
remember it.

If the user tells you their goal,
remember it.

Ask only ONE relevant question at a time.

Keep responses short.

Be friendly.

Be encouraging.

Do not sound robotic.

Do not behave like a textbook.

Do not give long explanations unless
the user asks for them.

==============================================
IMPORTANT
==============================================

Do not use tools.

Do not generate tool calls.

Return ONLY the normal conversational
response that should be shown to the user.
"""


# ==========================================
# CONVERSATION MEMORY
# ==========================================

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


# ==========================================
# LANGUAGE DETECTION
# ==========================================

def detect_language(text):

    text = text.lower().strip()

    # Hindi Devanagari
    hindi_chars = 0

    for char in text:

        if "\u0900" <= char <= "\u097F":
            hindi_chars += 1

    if hindi_chars >= 2:
        return "hindi"


    # Common Hinglish words
    hinglish_words = {
        "mujhe",
        "mera",
        "meri",
        "mere",
        "main",
        "mai",
        "aap",
        "ap",
        "tum",
        "hum",
        "hai",
        "hain",
        "ho",
        "kar",
        "raha",
        "rahi",
        "rahe",
        "jana",
        "jaana",
        "college",
        "kal",
        "aaj",
        "kya",
        "kaise",
        "kaisa",
        "kaisi",
        "kyu",
        "kyun",
        "bahut",
        "acha",
        "achha",
        "pasand",
        "chahiye",
        "karna",
        "karni",
        "karne",
        "padhna",
        "padh",
        "bana",
        "bana",
        "wala",
        "wali"
    }

    words = set(text.split())

    matches = len(words.intersection(hinglish_words))

    if matches >= 1:
        return "hinglish"


    return "english"


# ==========================================
# LANGUAGE INSTRUCTION
# ==========================================

def get_language_instruction():

    if language_mode == "english":

        return """
LANGUAGE STYLE: ENGLISH

Reply in simple natural English.
"""


    if language_mode == "hindi":

        return """
LANGUAGE STYLE: HINDI

Reply primarily in Hindi using
Devanagari script.
"""


    if language_mode == "hinglish":

        return """
LANGUAGE STYLE: HINGLISH

Reply naturally in Hinglish.

Use Roman Hindi mixed with English.

Do NOT reply only in English.

Example:
Main bas aapse baat kar raha hoon!
Aur aap kya kar rahe ho?
"""


    return """
LANGUAGE STYLE: AUTO

Automatically match the user's
language style naturally.
"""


# ==========================================
# UPDATE LANGUAGE
# ==========================================

def set_language(mode):

    global language_mode

    language_mode = mode

    # Remove previous language messages
    global messages

    messages = [
        message
        for message in messages
        if not (
            message["role"] == "system"
            and message["content"].startswith(
                "LANGUAGE STYLE:"
            )
        )
    ]

    messages.append(
        {
            "role": "system",
            "content": get_language_instruction()
        }
    )


# ==========================================
# LIMIT MEMORY
# ==========================================

def limit_history():

    global messages

    system_messages = [
        message
        for message in messages
        if message["role"] == "system"
    ]

    conversation_messages = [
        message
        for message in messages
        if message["role"] != "system"
    ]

    conversation_messages = conversation_messages[
        -MAX_HISTORY:
    ]

    messages = (
        system_messages
        + conversation_messages
    )


# ==========================================
# GENERATE RESPONSE
# ==========================================

def generate_response(user_message):

    global messages

    # Detect language automatically
    if language_mode == "auto":

        detected = detect_language(
            user_message
        )

        # Update temporary language instruction
        messages.append(
            {
                "role": "system",
                "content":
                    f"CURRENT USER LANGUAGE: {detected.upper()}\n"
                    f"Reply naturally in {detected}."
            }
        )


    # Add user message
    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    # Keep history under control
    limit_history()


    # --------------------------------------
    # API REQUEST
    # --------------------------------------

    last_error = None

    for attempt in range(3):

        try:

            response = client.chat_completion(

                model=MODEL_NAME,

                messages=messages,

                max_tokens=250,

                temperature=0.7,

                tools=[]
            )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

            if answer:

                answer = answer.strip()

                messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                # Remove temporary auto-language
                # instruction
                if language_mode == "auto":

                    messages[:] = [
                        message
                        for message in messages
                        if not (
                            message["role"] == "system"
                            and message["content"].startswith(
                                "CURRENT USER LANGUAGE:"
                            )
                        )
                    ]

                return answer


        except Exception as error:

            last_error = error

            # Wait before retry
            if attempt < 2:

                time.sleep(2)


    # --------------------------------------
    # FAILURE
    # --------------------------------------

    # Remove failed user message
    if messages:

        if messages[-1]["role"] == "user":

            messages.pop()


    raise last_error


# ==========================================
# CLEAR CONVERSATION
# ==========================================

def clear_conversation():

    global messages

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if language_mode != "auto":

        messages.append(
            {
                "role": "system",
                "content":
                    get_language_instruction()
            }
        )


# ==========================================
# START SPEAKWISE
# ==========================================

print("==========================================")
print("             SPEAKWISE AI")
print("      NATURAL CONVERSATION PARTNER")
print("==========================================")

print()

print(
    "🤖 SpeakWise: Hi! I'm SpeakWise. 😊"
)

print(
    "Let's practice communication together!"
)

print()

print(
    "I can naturally understand English, "
    "Hindi and Hinglish."
)

print()

print("Commands:")

print("  /english")
print("  /hindi")
print("  /hinglish")
print("  /auto")
print("  /mode")
print("  /clear")
print("  exit")


# ==========================================
# CHAT LOOP
# ==========================================

while True:

    try:

        user_message = input(
            "\n👤 You: "
        ).strip()


        # ==================================
        # EMPTY
        # ==================================

        if not user_message:

            print(
                "⚠️ Please enter something."
            )

            continue


        command = user_message.lower()


        # ==================================
        # EXIT
        # ==================================

        if command == "exit":

            print()

            print(
                "🤖 SpeakWise: "
                "Great talking with you! 😊"
            )

            print(
                "Keep practicing English. "
                "See you next time! 👋"
            )

            break


        # ==================================
        # ENGLISH
        # ==================================

        if command in [
            "english",
            "/english",
            "speak english",
            "speak in english",
            "talk in english",
            "english mode"
        ]:

            set_language("english")

            print()

            print(
                "🤖 SpeakWise: "
                "Sure! Ab English mein baat karte hain. 🇬🇧"
            )

            continue


        # ==================================
        # HINDI
        # ==================================

        if command in [
            "hindi",
            "/hindi",
            "speak hindi",
            "speak in hindi",
            "talk in hindi",
            "hindi mode"
        ]:

            set_language("hindi")

            print()

            print(
                "🤖 SpeakWise: "
                "ठीक है! अब हम हिंदी में बात करेंगे। 🇮🇳"
            )

            continue


        # ==================================
        # HINGLISH
        # ==================================

        if command in [
            "hinglish",
            "/hinglish",
            "speak hinglish",
            "speak in hinglish",
            "talk in hinglish",
            "hinglish mode"
        ]:

            set_language("hinglish")

            print()

            print(
                "🤖 SpeakWise: "
                "Bilkul! Ab Hinglish mein baat karte hain. 🗣️"
            )

            continue


        # ==================================
        # AUTO MODE
        # ==================================

        if command in [
            "auto",
            "/auto",
            "automatic",
            "auto mode"
        ]:

            set_language("auto")

            print()

            print(
                "🤖 SpeakWise: "
                "Okay! Ab main aapki language "
                "automatically samajhunga. 😊"
            )

            continue


        # ==================================
        # MODE
        # ==================================

        if command in [
            "mode",
            "/mode"
        ]:

            print()

            if language_mode == "auto":

                print(
                    "🤖 SpeakWise: "
                    "Current mode: AUTO"
                )

                print(
                    "I'll naturally detect "
                    "English, Hindi or Hinglish."
                )

            else:

                print(
                    "🤖 SpeakWise: "
                    "Current mode:",
                    language_mode.upper()
                )

            continue


        # ==================================
        # CLEAR
        # ==================================

        if command == "/clear":

            clear_conversation()

            print()

            print(
                "🤖 SpeakWise: "
                "Conversation cleared! 🧹"
            )

            continue


        # ==================================
        # IGNORE TERMINAL COMMANDS
        # ==================================

        if (
            "python -u" in command
            or "python nlp/" in command
            or "conversation.py" in command
        ):

            print()

            print(
                "🤖 SpeakWise: "
                "That looks like a Python command. "
                "You can run it directly in PowerShell."
            )

            continue


        # ==================================
        # AI RESPONSE
        # ==================================

        print(
            "\n🤖 SpeakWise: ",
            end=""
        )

        answer = generate_response(
            user_message
        )

        print(answer)


    # ======================================
    # ERROR
    # ======================================

    except Exception as error:

        print()

        print(
            "❌ SpeakWise temporarily "
            "couldn't generate a response."
        )

        print(
            "Error:",
            error
        )

        print(
            "\nPlease try the message again."
        )


    # ======================================
    # CTRL+C
    # ======================================

    except KeyboardInterrupt:

        print()

        print(
            "\n🤖 SpeakWise: Goodbye! 👋"
        )

        break