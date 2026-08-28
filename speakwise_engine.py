import sys
import os
import re


# ==================================================
# PROJECT PATH
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ==================================================
# NLP IMPORT
# ==================================================

from nlp.learning_assistant import analyze_sentence


# ==================================================
# COMMON ENGLISH WORDS
# ==================================================

COMMON_WORDS = {
    "i",
    "am",
    "is",
    "are",
    "was",
    "were",
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "to",
    "of",
    "in",
    "on",
    "at",
    "for",
    "from",
    "with",
    "my",
    "me",
    "you",
    "your",
    "he",
    "she",
    "it",
    "we",
    "they",
    "this",
    "that",
    "these",
    "those",
    "hello",
    "hi",
    "how",
    "what",
    "where",
    "when",
    "why",
    "who",
    "can",
    "could",
    "will",
    "would",
    "should",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "go",
    "going",
    "come",
    "coming",
    "want",
    "need",
    "like",
    "love",
    "college",
    "school",
    "student",
    "study",
    "studying",
    "learn",
    "learning",
    "project",
    "today",
    "tomorrow",
    "yesterday",
    "good",
    "fine",
    "great",
    "name",
    "myself",
    "about",
    "please",
    "thank",
    "thanks",
    "yes",
    "no",
    "not",
    "know",
    "think",
    "working",
    "work",
    "computer",
    "python",
    "artificial",
    "intelligence",
    "data",
    "science",
    "machine",
    "learning",
}


# ==================================================
# KNOWN GARBAGE PATTERNS
# ==================================================

GARBAGE_PATTERNS = {
    "qwer",
    "qwerty",
    "asdf",
    "asdfgh",
    "sdf",
    "zxc",
    "zxcv",
    "zxcvb",
    "ert",
    "ertyu",
}


# ==================================================
# INPUT VALIDATION
# ==================================================

def is_meaningful_input(sentence):
    """
    Determines whether the user's input looks
    like meaningful language.
    """

    text = sentence.strip().lower()

    # Empty input
    if not text:
        return False

    # ----------------------------------------------
    # Explicit garbage words
    # ----------------------------------------------

    for pattern in GARBAGE_PATTERNS:

        if pattern in text:
            return False

    # ----------------------------------------------
    # Extract alphabetic words
    # ----------------------------------------------

    words = re.findall(
        r"[a-zA-Z]+",
        text
    )

    # No words
    if not words:
        return False

    # ----------------------------------------------
    # Reject mixed keyboard garbage
    # Example:
    # ert7u8
    # ----------------------------------------------

    if re.search(
        r"[a-zA-Z]+\d+[a-zA-Z]*",
        text
    ):
        return False

    # ----------------------------------------------
    # Single word
    # ----------------------------------------------

    if len(words) == 1:

        word = words[0]

        # Known English word
        if word in COMMON_WORDS:
            return True

        # Very short unknown word
        if len(word) <= 3:
            return False

        # Check suspicious consonant pattern
        vowels = set("aeiou")

        vowel_count = sum(
            1 for char in word
            if char in vowels
        )

        # A normal word generally contains vowels.
        # This helps reject strings like:
        # sdf, qwr, zxcv
        if vowel_count == 0:
            return False

        return True

    # ----------------------------------------------
    # Multiple words
    # ----------------------------------------------

    meaningful_words = 0

    for word in words:

        if word in COMMON_WORDS:

            meaningful_words += 1

            continue

        # Unknown words can still be:
        # names, places, technical terms, etc.

        if len(word) >= 4:

            vowels = set("aeiou")

            vowel_count = sum(
                1 for char in word
                if char in vowels
            )

            if vowel_count > 0:
                meaningful_words += 1

    # At least one meaningful-looking word
    if meaningful_words >= 1:
        return True

    return False


# ==================================================
# INVALID INPUT RESPONSE
# ==================================================

def invalid_result(sentence):

    return {
        "success": True,

        "input": sentence,

        "analysis": {

            "valid": False,

            "message": (
                "I couldn't understand that clearly. "
                "Please try a meaningful sentence."
            ),

            "grammar": {
                "error_count": 0,
                "errors": [],
                "corrections": []
            },

            "vocabulary": {
                "word_count": 0,
                "suspicious_words": []
            },

            "features": {
                "word_count": 0,
                "unique_words": 0,
                "word_diversity": 0.0,
                "avg_word_length": 0.0,
                "repeated_word_ratio": 0.0,
                "long_word_ratio": 0.0
            },

            "fluency_score": 0
        }
    }


# ==================================================
# MAIN ANALYSIS ENGINE
# ==================================================

def analyze(message):

    """
    Main SpeakWise learning analysis engine.
    """

    message = message.strip()

    # ----------------------------------------------
    # Empty input
    # ----------------------------------------------

    if not message:

        return {
            "success": False,
            "message": "Please enter something."
        }

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    if not is_meaningful_input(message):

        return invalid_result(message)

    # ----------------------------------------------
    # NORMAL NLP ANALYSIS
    # ----------------------------------------------

    try:

        result = analyze_sentence(
            message
        )

        # Add valid flag without changing
        # existing NLP output.

        result["valid"] = True

        return {
            "success": True,
            "input": message,
            "analysis": result
        }

    except Exception as error:

        return {
            "success": False,
            "input": message,
            "error": str(error)
        }


# ==================================================
# DIRECT TESTING
# ==================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("          SPEAKWISE ENGINE")
    print("==========================================")
    print()

    while True:

        sentence = input(
            "Enter a sentence: "
        ).strip()

        if sentence.lower() == "exit":
            print()
            print("SpeakWise Engine stopped.")
            break

        result = analyze(sentence)

        print()
        print(result)
        print()