import re


def extract_features(sentence):

    text = sentence.lower().strip()

    words = re.findall(r"\b[a-zA-Z]+\b", text)

    total_words = len(words)

    if total_words == 0:
        return {
            "word_count": 0,
            "unique_words": 0,
            "word_diversity": 0,
            "avg_word_length": 0,
            "repeated_word_ratio": 0,
            "long_word_ratio": 0
        }

    unique_words = len(set(words))

    word_diversity = unique_words / total_words

    avg_word_length = (
        sum(len(word) for word in words)
        / total_words
    )

    repeated_word_ratio = (
        total_words - unique_words
    ) / total_words

    long_words = [
        word for word in words
        if len(word) >= 6
    ]

    long_word_ratio = (
        len(long_words) / total_words
    )

    return {
        "word_count": total_words,
        "unique_words": unique_words,
        "word_diversity": round(word_diversity, 2),
        "avg_word_length": round(avg_word_length, 2),
        "repeated_word_ratio": round(
            repeated_word_ratio, 2
        ),
        "long_word_ratio": round(
            long_word_ratio, 2
        )
    }


def detect_basic_errors(sentence):

    text = sentence.strip()

    errors = []

    # I am
    if re.search(r"\biam\b", text, re.IGNORECASE):
        errors.append(
            "Write 'I am' instead of 'iam'."
        )

    # I has
    if re.search(r"\bI\s+has\b", text, re.IGNORECASE):
        errors.append(
            "Use 'I have' instead of 'I has'."
        )

    # She are / He are
    if re.search(
        r"\b(She|He|It)\s+are\b",
        text,
        re.IGNORECASE
    ):
        errors.append(
            "Use 'is' with he, she, or it."
        )

    # They is
    if re.search(
        r"\bThey\s+is\b",
        text,
        re.IGNORECASE
    ):
        errors.append(
            "Use 'are' with they."
        )

    # I am + base verb
    if re.search(
        r"\bI\s+am\s+(go|eat|play|study|read|write)\b",
        text,
        re.IGNORECASE
    ):
        errors.append(
            "After 'I am', use the -ing form."
        )

    return errors


# ==========================================
# SPEAKWISE COMPLETE ANALYZER
# ==========================================

sentence = input(
    "Enter an English sentence: "
)

features = extract_features(sentence)

errors = detect_basic_errors(sentence)


print("\n================================")
print("       SPEAKWISE ANALYSIS")
print("================================")

print("\nSentence:")
print(sentence)


print("\n--- Language Features ---")

for name, value in features.items():

    print(
        f"{name}: {value}"
    )


print("\n--- Grammar Analysis ---")

if errors:

    print("❌ Problems found:")

    for error in errors:

        print("-", error)

else:

    print("✅ No basic grammar errors detected.")


print("\n--- Summary ---")

print(
    "Grammar errors:",
    len(errors)
)

print(
    "Vocabulary diversity:",
    features["word_diversity"]
)