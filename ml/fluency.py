import re


def calculate_features(sentence):

    text = sentence.lower().strip()

    words = re.findall(r"\b[a-zA-Z]+\b", text)

    total_words = len(words)

    if total_words == 0:
        return {
            "word_count": 0,
            "unique_words": 0,
            "word_diversity": 0,
            "avg_word_length": 0,
            "sentence_complexity": 0,
            "repeated_word_ratio": 0,
            "long_word_ratio": 0
        }

    # Unique words
    unique_words = len(set(words))

    # Vocabulary diversity
    word_diversity = unique_words / total_words

    # Average word length
    avg_word_length = sum(
        len(word) for word in words
    ) / total_words

    # Long words (6+ characters)
    long_words = [
        word for word in words
        if len(word) >= 6
    ]

    long_word_ratio = len(long_words) / total_words

    # Repeated words
    repeated_word_ratio = (
        total_words - unique_words
    ) / total_words

    # Sentence complexity
    conjunctions = [
        "and",
        "but",
        "because",
        "although",
        "while",
        "however",
        "which",
        "that"
    ]

    conjunction_count = sum(
        text.count(word)
        for word in conjunctions
    )

    sentence_complexity = conjunction_count + 1

    return {

        "word_count": total_words,

        "unique_words": unique_words,

        "word_diversity": round(
            word_diversity, 2
        ),

        "avg_word_length": round(
            avg_word_length, 2
        ),

        "sentence_complexity":
            sentence_complexity,

        "repeated_word_ratio": round(
            repeated_word_ratio, 2
        ),

        "long_word_ratio": round(
            long_word_ratio, 2
        )
    }


# =========================================
# TEST
# =========================================

sentence = input(
    "Enter an English sentence: "
)

features = calculate_features(sentence)

print("\n--- SpeakWise Language Features ---")

for feature, value in features.items():

    print(
        f"{feature}: {value}"
    )