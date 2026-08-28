import os

from openhinglish import normalize
from huggingface_hub import InferenceClient


# ==========================================
# HUGGING FACE CLIENT
# ==========================================

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("❌ HF_TOKEN is not configured.")
    exit()


client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN
)


# ==========================================
# HINGLISH → HINDI
# ==========================================

def hinglish_to_hindi(text):

    result = normalize(text)

    return result.display, result.confidence


# ==========================================
# HINDI → ENGLISH
# ==========================================

def hindi_to_english(text):

    result = client.translation(
        text,
        model="Helsinki-NLP/opus-mt-hi-en"
    )

    return result.translation_text


# ==========================================
# COMPLETE TRANSLATION
# ==========================================

def translate_to_english(text):

    # Convert Roman Hindi/Hinglish
    # into Devanagari Hindi

    hindi, confidence = hinglish_to_hindi(
        text
    )

    # Translate Hindi → English

    english = hindi_to_english(
        hindi
    )

    return hindi, confidence, english


# ==========================================
# SPEAKWISE TRANSLATOR
# ==========================================

print("================================")
print("     SPEAKWISE TRANSLATOR")
print("================================")

text = input(
    "\nEnter Hindi / Hinglish: "
)


try:

    hindi, confidence, english = (
        translate_to_english(text)
    )

    print("\n--------------------------------")
    print("Translation Result")
    print("--------------------------------")

    print("\nInput:")
    print(text)

    print("\n🇮🇳 Hindi:")
    print(hindi)

    print("\nConfidence:")
    print(round(confidence, 2))

    print("\n🇬🇧 English:")
    print(english)

except Exception as error:

    print("\n❌ Translation failed.")
    print("Error:", error)