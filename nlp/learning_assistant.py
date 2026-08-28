import re
from collections import Counter

try:
    # Used when SpeakWise is started from the project root
    from nlp.analyzer import analyze_grammar
except ModuleNotFoundError:
    # Used when learning_assistant.py is run directly
    from nlp.analyzer import analyze_grammar


# ==========================================
# SPEAKWISE LEARNING ASSISTANT
# ==========================================


# ==========================================
# COMMON ENGLISH WORDS
# ==========================================

COMMON_WORDS = {
    "i", "you", "he", "she", "it", "we", "they",
    "am", "is", "are", "was", "were",
    "have", "has", "had",
    "do", "does", "did",

    "go", "went", "going",
    "come", "came", "coming",

    "want", "need", "like", "love",

    "study", "studying",
    "learn", "learning",

    "college", "school", "student",

    "my", "your", "his", "her",
    "our", "their",

    "the", "a", "an",

    "to", "from", "in", "on", "at",
    "for", "with", "and", "or", "but",

    "because",
    "today", "tomorrow", "yesterday",

    "what", "where", "when",
    "why", "how",

    "good", "bad", "great", "fine",

    "football", "cricket",

    "english", "python",

    "artificial", "intelligence",

    "data", "science", "scientist",

    "machine", "learning",

    "project", "communication",

    "technology", "engineering",

    "name", "about", "work",
    "working", "practice",
    "practicing",

    "hello", "hi",
    "thanks", "thank",
    "please",

    "can", "could",
    "will", "would",
    "should",

    "not", "no", "yes",

    "know", "think",
    "talk", "speak",
    "read", "write",
    "play", "eat",
    "run", "walk",
    "sleep",

    "computer",
    "programming",
    "software"
}


# ==========================================
# PROPER NAMES / PLACES / SPECIAL WORDS
# ==========================================

KNOWN_NAMES = {
    "rehan",
    "mohammad",
    "tabish",
    "buldhana",
    "pune",
    "messi",
    "mess"
}


# ==========================================
# INVALID / GARBAGE PATTERNS
# ==========================================

GARBAGE_PATTERNS = {
    "qwer",
    "qwerty",
    "asdf",
    "asdfgh",
    "sdf",
    "zxc",
    "zxcv",
    "zxcvb",
    "werty",
    "wertyui"
}


# ==========================================
# INPUT VALIDATION
# ==========================================

def is_meaningful_input(sentence):

    text = sentence.strip().lower()

    if not text:
        return False

    # --------------------------------------
    # Explicit garbage patterns
    # --------------------------------------

    for pattern in GARBAGE_PATTERNS:

        if pattern in text:
            return False


    # --------------------------------------
    # Reject mixed keyboard/number garbage
    # Example:
    # ert7u8
    # --------------------------------------

    if re.search(
        r"[a-zA-Z]+\d+[a-zA-Z]*",
        text
    ):

        return False


    # --------------------------------------
    # Extract words
    # --------------------------------------

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    if not words:
        return False


    # --------------------------------------
    # Single word
    # --------------------------------------

    if len(words) == 1:

        word = words[0]

        if word in COMMON_WORDS:
            return True

        if word in KNOWN_NAMES:
            return True

        # Very short unknown word
        if len(word) <= 3:
            return False

        # Check vowels
        vowels = set("aeiou")

        vowel_count = sum(
            1
            for char in word
            if char in vowels
        )

        # Strings such as:
        # sdf
        # qwr
        # zxcv
        # should fail
        if vowel_count == 0:
            return False

        return True


    # --------------------------------------
    # Multiple words
    # --------------------------------------

    meaningful_words = 0

    for word in words:

        if word in COMMON_WORDS:

            meaningful_words += 1
            continue


        if word in KNOWN_NAMES:

            meaningful_words += 1
            continue


        # Unknown words can be names,
        # places or technical terms.

        if len(word) >= 4:

            vowels = set("aeiou")

            vowel_count = sum(
                1
                for char in word
                if char in vowels
            )

            if vowel_count > 0:

                meaningful_words += 1


    return meaningful_words >= 1


# ==========================================
# INVALID RESULT
# ==========================================

def invalid_analysis(sentence):

    return {

        "valid": False,

        "message": (
            "I couldn't understand that clearly. "
            "Please try a meaningful sentence."
        ),

        "grammar": {

            "error_count": 0,

            "errors": [],

            "suggestions": [],

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


# ==========================================
# VOCABULARY ANALYSIS
# ==========================================

def vocabulary_analysis(sentence):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        sentence.lower()
    )

    suspicious = []

    for word in words:

        if (
            len(word) >= 4
            and word not in COMMON_WORDS
            and word not in KNOWN_NAMES
        ):

            suspicious.append(word)


    return {

        "word_count": len(words),

        "suspicious_words": suspicious
    }


# ==========================================
# LANGUAGE FEATURES
# ==========================================

def language_features(sentence):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        sentence.lower()
    )

    word_count = len(words)


    if word_count == 0:

        return {

            "word_count": 0,

            "unique_words": 0,

            "word_diversity": 0.0,

            "avg_word_length": 0.0,

            "repeated_word_ratio": 0.0,

            "long_word_ratio": 0.0
        }


    unique_words = len(
        set(words)
    )


    word_diversity = (
        unique_words / word_count
    )


    avg_word_length = (
        sum(
            len(word)
            for word in words
        )
        / word_count
    )


    counts = Counter(words)


    repeated_words = sum(
        1
        for word, count in counts.items()
        if count > 1
    )


    repeated_word_ratio = (
        repeated_words / word_count
    )


    long_words = sum(
        1
        for word in words
        if len(word) >= 7
    )


    long_word_ratio = (
        long_words / word_count
    )


    return {

        "word_count": word_count,

        "unique_words": unique_words,

        "word_diversity": round(
            word_diversity,
            2
        ),

        "avg_word_length": round(
            avg_word_length,
            2
        ),

        "repeated_word_ratio": round(
            repeated_word_ratio,
            2
        ),

        "long_word_ratio": round(
            long_word_ratio,
            2
        )
    }


# ==========================================
# FLUENCY SCORE
# ==========================================

def calculate_fluency(
    features,
    grammar_errors
):

    score = 50


    # --------------------------------------
    # More words
    # --------------------------------------

    if features["word_count"] >= 5:

        score += 10


    if features["word_count"] >= 10:

        score += 5


    # --------------------------------------
    # Vocabulary diversity
    # --------------------------------------

    if features["word_diversity"] >= 0.8:

        score += 10

    elif features["word_diversity"] >= 0.6:

        score += 5


    # --------------------------------------
    # Grammar errors
    # --------------------------------------

    score -= grammar_errors * 8


    # --------------------------------------
    # Keep between 0 and 100
    # --------------------------------------

    score = max(
        0,
        min(100, score)
    )


    return score


# ==========================================
# OVERALL ANALYSIS
# ==========================================

def analyze_sentence(sentence):

    sentence = sentence.strip()


    # ======================================
    # INPUT VALIDATION
    # ======================================

    if not is_meaningful_input(sentence):

        return invalid_analysis(
            sentence
        )


    # ======================================
    # GRAMMAR
    # ======================================

    grammar = analyze_grammar(
        sentence
    )


    # ======================================
    # VOCABULARY
    # ======================================

    vocabulary = vocabulary_analysis(
        sentence
    )


    # ======================================
    # LANGUAGE FEATURES
    # ======================================

    features = language_features(
        sentence
    )


    # ======================================
    # FLUENCY
    # ======================================

    fluency = calculate_fluency(

        features,

        grammar["error_count"]
    )


    # ======================================
    # FINAL RESULT
    # ======================================

    return {

        "valid": True,

        "grammar": grammar,

        "vocabulary": vocabulary,

        "features": features,

        "fluency_score": fluency
    }


# ==========================================
# DISPLAY ANALYSIS
# ==========================================

def display_analysis(
    sentence,
    result
):

    print()

    print(
        "------------------------------------------"
    )

    print(
        "        SPEAKWISE LEARNING ANALYSIS"
    )

    print(
        "------------------------------------------"
    )


    # ======================================
    # INVALID INPUT
    # ======================================

    if not result.get("valid", True):

        print()

        print(
            "⚠️ LOW CONFIDENCE"
        )

        print()

        print(
            result.get(
                "message",
                "Input could not be understood."
            )
        )

        print()

        print(
            "💡 Please try a clearer sentence."
        )

        print()

        print(
            "Example:"
        )

        print(
            "mujhe kal college jana hai"
        )

        return


    # ======================================
    # GRAMMAR
    # ======================================

    print()

    print("--- Grammar ---")


    grammar = result["grammar"]


    if grammar["error_count"] == 0:

        print(
            "✅ No basic grammar errors detected."
        )

    else:

        for error in grammar["errors"]:

            print(
                "❌",
                error
            )


        if grammar.get("suggestions"):

            print()

            print(
                "💡 Suggestions:"
            )

            for suggestion in grammar["suggestions"]:

                print(
                    "-",
                    suggestion
                )


        if grammar.get("corrections"):

            print()

            print(
                "✏️ Corrections:"
            )

            for correction in grammar["corrections"]:

                print(
                    "-",
                    correction
                )


    # ======================================
    # VOCABULARY
    # ======================================

    print()

    print("--- Vocabulary ---")


    suspicious = (
        result["vocabulary"]
        ["suspicious_words"]
    )


    if not suspicious:

        print(
            "✅ No suspicious words detected."
        )

    else:

        for word in suspicious:

            print(
                "⚠️ Suspicious word:",
                word
            )


    # ======================================
    # LANGUAGE FEATURES
    # ======================================

    print()

    print(
        "--- Language Features ---"
    )


    features = result["features"]


    for key, value in features.items():

        print(
            f"{key}: {value}"
        )


    # ======================================
    # FLUENCY
    # ======================================

    print()

    print("--- Fluency ---")

    print(
        f"Fluency score: "
        f"{result['fluency_score']}/100"
    )


# ==========================================
# TEST MODE
# ==========================================

if __name__ == "__main__":

    print(
        "=========================================="
    )

    print(
        "       SPEAKWISE LEARNING ASSISTANT"
    )

    print(
        "=========================================="
    )

    print()


    sentence = input(
        "Enter an English sentence: "
    ).strip()


    if not sentence:

        print(
            "❌ Please enter a sentence."
        )

    else:

        result = analyze_sentence(
            sentence
        )


        print()

        print(
            "Sentence:"
        )

        print(sentence)


        display_analysis(
            sentence,
            result
        )


        print()

        print(
            "------------------------------------------"
        )

        print(
            "             ANALYSIS COMPLETE"
        )

        print(
            "------------------------------------------"
        )