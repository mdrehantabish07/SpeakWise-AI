import os
import re

from openhinglish import normalize
from huggingface_hub import InferenceClient
from wordfreq import zipf_frequency


# ==========================================
# CONFIGURATION
# ==========================================

CONFIDENCE_THRESHOLD = 0.60

MODEL_NAME = "Helsinki-NLP/opus-mt-hi-en"


# ==========================================
# HUGGING FACE CLIENT
# ==========================================

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:

    print("❌ HF_TOKEN is not configured.")

    raise SystemExit


client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN
)


# ==========================================
# HINGLISH → HINDI
# ==========================================

def hinglish_to_hindi(text):

    result = normalize(text)

    hindi = result.display

    confidence = float(
        result.confidence
    )

    return hindi, confidence


# ==========================================
# HINDI → ENGLISH
# ==========================================

def hindi_to_english(text):

    result = client.translation(
        text,
        model=MODEL_NAME
    )

    return result.translation_text.strip()


# ==========================================
# GRAMMAR ANALYSIS
# ==========================================

def grammar_analysis(sentence):

    errors = []

    if re.search(
        r"\biam\b",
        sentence,
        re.IGNORECASE
    ):

        errors.append(
            "Write 'I am' instead of 'iam'."
        )


    if re.search(
        r"\bI\s+has\b",
        sentence,
        re.IGNORECASE
    ):

        errors.append(
            "Use 'I have' instead of 'I has'."
        )


    if re.search(
        r"\b(She|He|It)\s+are\b",
        sentence,
        re.IGNORECASE
    ):

        errors.append(
            "Use 'is' with he, she, or it."
        )


    if re.search(
        r"\bThey\s+is\b",
        sentence,
        re.IGNORECASE
    ):

        errors.append(
            "Use 'are' with they."
        )


    if re.search(
        r"\bI\s+am\s+(go|eat|play|study|read|write)\b",
        sentence,
        re.IGNORECASE
    ):

        errors.append(
            "After 'I am', use the -ing form."
        )


    return errors


# ==========================================
# VOCABULARY
# ==========================================

def vocabulary_analysis(sentence):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        sentence.lower()
    )

    suspicious = []

    for word in words:

        frequency = zipf_frequency(
            word,
            "en"
        )

        if frequency == 0:

            suspicious.append(word)

    return suspicious


# ==========================================
# LANGUAGE FEATURES
# ==========================================

def language_features(sentence):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        sentence.lower()
    )

    if not words:

        return {}


    total = len(words)

    unique = len(set(words))


    return {

        "word_count":
            total,

        "unique_words":
            unique,

        "word_diversity":
            round(
                unique / total,
                2
            ),

        "avg_word_length":
            round(
                sum(
                    len(word)
                    for word in words
                ) / total,
                2
            ),

        "repeated_word_ratio":
            round(
                (total - unique)
                / total,
                2
            ),

        "long_word_ratio":
            round(
                len([
                    word
                    for word in words
                    if len(word) >= 6
                ]) / total,
                2
            )
    }


# ==========================================
# MAIN PROCESSING
# ==========================================

def process_sentence(text):

    # --------------------------------------
    # STEP 1
    # Hinglish → Hindi
    # --------------------------------------

    hindi, confidence = (
        hinglish_to_hindi(text)
    )


    # --------------------------------------
    # STEP 2
    # CONFIDENCE CHECK
    # --------------------------------------

    if confidence < CONFIDENCE_THRESHOLD:

        return {

            "input":
                text,

            "hindi":
                hindi,

            "confidence":
                confidence,

            "english":
                None,

            "grammar_errors":
                [],

            "suspicious_words":
                [],

            "features":
                {},

            "low_confidence":
                True
        }


    # --------------------------------------
    # STEP 3
    # Hindi → English
    # --------------------------------------

    english = hindi_to_english(
        hindi
    )


    # --------------------------------------
    # STEP 4
    # Grammar
    # --------------------------------------

    grammar_errors = (
        grammar_analysis(
            english
        )
    )


    # --------------------------------------
    # STEP 5
    # Vocabulary
    # --------------------------------------

    suspicious_words = (
        vocabulary_analysis(
            english
        )
    )


    # --------------------------------------
    # STEP 6
    # Features
    # --------------------------------------

    features = (
        language_features(
            english
        )
    )


    return {

        "input":
            text,

        "hindi":
            hindi,

        "confidence":
            confidence,

        "english":
            english,

        "grammar_errors":
            grammar_errors,

        "suspicious_words":
            suspicious_words,

        "features":
            features,

        "low_confidence":
            False
    }


# ==========================================
# SPEAKWISE
# ==========================================

print("==========================================")

print(
    "              SPEAKWISE AI"
)

print(
    "      ENGLISH LEARNING PLATFORM"
)

print("==========================================")


text = input(
    "\n🇮🇳 Enter Hindi / Hinglish: "
)


# ==========================================
# RUN
# ==========================================

try:

    result = process_sentence(
        text
    )


    # ======================================
    # RESULT
    # ======================================

    print(
        "\n=========================================="
    )

    print(
        "                 RESULT"
    )

    print(
        "=========================================="
    )


    print("\n🇮🇳 Hindi:")

    print(
        result["hindi"]
    )


    print(
        "\n🔄 Hindi Confidence:",
        round(
            result["confidence"],
            2
        )
    )


    # ======================================
    # LOW CONFIDENCE
    # ======================================

    if result["low_confidence"]:

        print(
            "\n⚠️ LOW CONFIDENCE"
        )

        print(
            "\nSpeakWise could not confidently "
            "understand this input."
        )

        print(
            "\n💡 Please try a clearer sentence."
        )

        print(
            "\nExample:"
        )

        print(
            "mujhe kal college jana hai"
        )


    # ======================================
    # NORMAL
    # ======================================

    else:

        print(
            "\n🇬🇧 English:"
        )

        print(
            result["english"]
        )


        # ----------------------------------
        # Grammar
        # ----------------------------------

        print(
            "\n--- Grammar ---"
        )


        if result[
            "grammar_errors"
        ]:

            for error in result[
                "grammar_errors"
            ]:

                print(
                    "❌",
                    error
                )

        else:

            print(
                "✅ No basic grammar problems detected."
            )


        # ----------------------------------
        # Vocabulary
        # ----------------------------------

        print(
            "\n--- Vocabulary ---"
        )


        if result[
            "suspicious_words"
        ]:

            for word in result[
                "suspicious_words"
            ]:

                print(
                    "⚠️ Suspicious word:",
                    word
                )

        else:

            print(
                "✅ No suspicious words detected."
            )


        # ----------------------------------
        # Features
        # ----------------------------------

        print(
            "\n--- Language Features ---"
        )


        for key, value in result[
            "features"
        ].items():

            print(
                f"{key}: {value}"
            )


    print(
        "\n=========================================="
    )

    print(
        "          ANALYSIS COMPLETE"
    )

    print(
        "=========================================="
    )


except Exception as error:

    print(
        "\n❌ SpeakWise pipeline failed."
    )

    print(
        "Error:",
        error
    )