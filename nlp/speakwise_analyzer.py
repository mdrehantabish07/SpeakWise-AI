import re

from wordfreq import zipf_frequency

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


# ==========================================
# 1. LOAD CORRECTION MODEL
# ==========================================

MODEL_NAME = "vennify/t5-base-grammar-correction"

print("Loading grammar correction model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

correction_model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
)

print("Correction model loaded successfully!")


# ==========================================
# 2. GRAMMAR ERROR DETECTION
# ==========================================

def detect_grammar_errors(sentence):

    errors = []

    if re.search(r"\biam\b", sentence, re.IGNORECASE):
        errors.append("Write 'I am' instead of 'iam'.")

    if re.search(r"\bI\s+has\b", sentence, re.IGNORECASE):
        errors.append("Use 'I have' instead of 'I has'.")

    if re.search(
        r"\b(She|He|It)\s+are\b",
        sentence,
        re.IGNORECASE
    ):
        errors.append("Use 'is' with he, she, or it.")

    if re.search(
        r"\bThey\s+is\b",
        sentence,
        re.IGNORECASE
    ):
        errors.append("Use 'are' with they.")

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
# 3. VOCABULARY ANALYSIS
# ==========================================

def analyze_vocabulary(sentence):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        sentence.lower()
    )

    suspicious_words = []

    for word in words:

        frequency = zipf_frequency(
            word,
            "en"
        )

        if frequency == 0:
            suspicious_words.append(word)

    return suspicious_words


# ==========================================
# 4. LANGUAGE FEATURES
# ==========================================

def calculate_features(sentence):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        sentence.lower()
    )

    if not words:
        return {
            "word_count": 0,
            "unique_words": 0,
            "word_diversity": 0,
            "avg_word_length": 0,
            "repeated_word_ratio": 0,
            "long_word_ratio": 0
        }

    total_words = len(words)
    unique_words = len(set(words))

    return {
        "word_count": total_words,
        "unique_words": unique_words,
        "word_diversity": round(
            unique_words / total_words, 2
        ),
        "avg_word_length": round(
            sum(len(word) for word in words)
            / total_words,
            2
        ),
        "repeated_word_ratio": round(
            (total_words - unique_words)
            / total_words,
            2
        ),
        "long_word_ratio": round(
            len([
                word for word in words
                if len(word) >= 6
            ]) / total_words,
            2
        )
    }


# ==========================================
# 5. PROTECT IMPORTANT WORDS
# ==========================================

def get_protected_words(sentence):

    words = re.findall(
        r"\b[A-Za-z]+\b",
        sentence
    )

    protected = []

    for word in words:

        # Capitalized words may be names/places
        if word[0].isupper():
            protected.append(word)

    return protected


# ==========================================
# 6. GRAMMAR CORRECTION
# ==========================================

def correct_sentence(sentence):

    protected_words = get_protected_words(
        sentence
    )

    input_text = "grammar: " + sentence

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=128,
        truncation=True
    )

    outputs = correction_model.generate(
        **inputs,
        max_length=128,
        num_beams=4,
        early_stopping=True
    )

    corrected = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    # --------------------------------------
    # Protect important capitalized words
    # --------------------------------------

    for word in protected_words:

        if word not in corrected:

            # Don't accept a correction that
            # completely removes an important word.
            return sentence, True

    return corrected, False


# ==========================================
# 7. COMPLETE ANALYSIS
# ==========================================

def analyze(sentence):

    grammar_errors = detect_grammar_errors(
        sentence
    )

    suspicious_words = analyze_vocabulary(
        sentence
    )

    features = calculate_features(
        sentence
    )

    corrected, correction_rejected = (
        correct_sentence(sentence)
    )

    return {
        "grammar_errors": grammar_errors,
        "suspicious_words": suspicious_words,
        "features": features,
        "corrected": corrected,
        "correction_rejected": correction_rejected
    }


# ==========================================
# 8. USER INPUT
# ==========================================

print("\n================================")
print("          SPEAKWISE AI")
print("================================")

sentence = input(
    "\nEnter an English sentence: "
)


# ==========================================
# 9. ANALYZE
# ==========================================

result = analyze(sentence)


# ==========================================
# 10. DISPLAY RESULTS
# ==========================================

print("\n================================")
print("       SPEAKWISE ANALYSIS")
print("================================")

print("\nOriginal:")
print(sentence)


# Grammar
print("\n--- Grammar ---")

if result["grammar_errors"]:

    for error in result["grammar_errors"]:
        print("❌", error)

else:

    print("✅ No basic grammar errors detected.")


# Vocabulary
print("\n--- Vocabulary ---")

if result["suspicious_words"]:

    for word in result["suspicious_words"]:
        print("⚠️ Suspicious word:", word)

else:

    print("✅ No suspicious words detected.")


# Features
print("\n--- Language Features ---")

for name, value in result["features"].items():

    print(f"{name}: {value}")


# Correction
print("\n--- Safe Grammar Correction ---")

if result["correction_rejected"]:

    print(
        "⚠️ AI correction was rejected because "
        "it may have changed an important word."
    )

    print("\nOriginal kept:")
    print(sentence)

else:

    print("Corrected:")
    print(result["corrected"])


print("\n================================")
print("        ANALYSIS COMPLETE")
print("================================")