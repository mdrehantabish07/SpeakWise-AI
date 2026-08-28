import re


# ==================================================
# SPEAKWISE GRAMMAR ANALYZER
# ==================================================

def analyze_grammar(sentence):

    errors = []
    suggestions = []
    corrections = []

    text = sentence.strip()

    # ----------------------------------------------
    # Empty input
    # ----------------------------------------------

    if not text:

        return {
            "sentence": text,
            "error_count": 0,
            "errors": [],
            "suggestions": [],
            "corrections": []
        }


    # ==============================================
    # RULE 1: I + is
    # ==============================================

    if re.search(
        r"\bI\s+is\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'I am' instead of 'I is'."
        )

        corrections.append(
            "I am"
        )


    # ==============================================
    # RULE 2: I + has
    # ==============================================

    if re.search(
        r"\bI\s+has\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'I have' instead of 'I has'."
        )

        corrections.append(
            "I have"
        )


    # ==============================================
    # RULE 3: I + are
    # ==============================================

    if re.search(
        r"\bI\s+are\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'I am' instead of 'I are'."
        )

        corrections.append(
            "I am"
        )


    # ==============================================
    # RULE 4: HE / SHE / IT + are
    # ==============================================

    if re.search(
        r"\b(She|He|It)\s+are\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'is' with he, she, or it."
        )

        corrections.append(
            "is"
        )


    # ==============================================
    # RULE 5: THEY + is
    # ==============================================

    if re.search(
        r"\bThey\s+is\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'are' with they."
        )

        corrections.append(
            "are"
        )


    # ==============================================
    # RULE 6: WE + is
    # ==============================================

    if re.search(
        r"\bWe\s+is\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'are' with we."
        )

        corrections.append(
            "are"
        )


    # ==============================================
    # RULE 7: YOU + is
    # ==============================================

    if re.search(
        r"\bYou\s+is\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'are' with you."
        )

        corrections.append(
            "are"
        )


    # ==============================================
    # RULE 8:
    # I AM + BASE VERB
    # ==============================================

    base_verbs = (
        "go|eat|play|study|read|write|"
        "work|come|run|walk|learn|"
        "watch|sleep|talk|speak|"
        "make|do|take|use|"
        "learn|practice"
    )

    match = re.search(
        rf"\bI\s+am\s+({base_verbs})\b",
        text,
        re.IGNORECASE
    )

    if match:

        verb = match.group(1)

        errors.append(
            "Verb form"
        )

        suggestions.append(
            "After 'I am', use the -ing form."
        )

        # Common verb conversions

        ing_forms = {
            "go": "going",
            "eat": "eating",
            "play": "playing",
            "study": "studying",
            "read": "reading",
            "write": "writing",
            "work": "working",
            "come": "coming",
            "run": "running",
            "walk": "walking",
            "learn": "learning",
            "watch": "watching",
            "sleep": "sleeping",
            "talk": "talking",
            "speak": "speaking",
            "make": "making",
            "do": "doing",
            "take": "taking",
            "use": "using",
            "practice": "practicing"
        }

        if verb.lower() in ing_forms:

            corrections.append(
                f"I am {ing_forms[verb.lower()]}"
            )


    # ==============================================
    # RULE 9:
    # I + DOES
    # ==============================================

    if re.search(
        r"\bI\s+does\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'do' instead of 'does' with I."
        )

        corrections.append(
            "I do"
        )


    # ==============================================
    # RULE 10:
    # I + DIDN'T + BASE VERB
    # ==============================================

    if re.search(
        r"\bI\s+didn't\s+\w+ed\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Verb form"
        )

        suggestions.append(
            "After 'didn't', use the base form of the verb."
        )


    # ==============================================
    # RULE 11:
    # HE / SHE + HAVE
    # ==============================================

    if re.search(
        r"\b(She|He|It)\s+have\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'has' with he, she, or it."
        )

        corrections.append(
            "has"
        )


    # ==============================================
    # RULE 12:
    # HE / SHE + DO
    # ==============================================

    if re.search(
        r"\b(She|He|It)\s+do\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Subject-verb agreement"
        )

        suggestions.append(
            "Use 'does' with he, she, or it."
        )

        corrections.append(
            "does"
        )


    # ==============================================
    # RULE 13:
    # I GO COLLEGE
    # ==============================================

    if re.search(
        r"\bI\s+go\s+college\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Missing preposition"
        )

        suggestions.append(
            "Say 'I go to college.'"
        )

        corrections.append(
            "I go to college"
        )


    # ==============================================
    # RULE 14:
    # I WANT GO
    # ==============================================

    if re.search(
        r"\bI\s+want\s+go\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Missing 'to'"
        )

        suggestions.append(
            "Use 'I want to go'."
        )

        corrections.append(
            "I want to go"
        )


    # ==============================================
    # RULE 15:
    # I LIKE GO
    # ==============================================

    if re.search(
        r"\bI\s+like\s+go\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Verb form"
        )

        suggestions.append(
            "Use 'I like going' or 'I like to go'."
        )


    # ==============================================
    # RULE 16:
    # IAM → I AM
    # ==============================================

    if re.search(
        r"\biam\b",
        text,
        re.IGNORECASE
    ):

        errors.append(
            "Word spacing"
        )

        suggestions.append(
            "Write 'I am' instead of 'iam'."
        )

        corrections.append(
            "I am"
        )


    # ==============================================
    # REMOVE DUPLICATE RESULTS
    # ==============================================

    errors = list(dict.fromkeys(errors))

    suggestions = list(
        dict.fromkeys(suggestions)
    )

    corrections = list(
        dict.fromkeys(corrections)
    )


    # ==============================================
    # FINAL RESULT
    # ==============================================

    result = {

        "sentence": text,

        "error_count": len(errors),

        "errors": errors,

        "suggestions": suggestions,

        "corrections": corrections
    }

    return result


# ==================================================
# TERMINAL TESTING
# ==================================================

if __name__ == "__main__":

    print()
    print("================================")
    print("     SPEAKWISE GRAMMAR")
    print("         ANALYZER")
    print("================================")

    sentence = input(
        "\nEnter an English sentence: "
    )

    result = analyze_grammar(
        sentence
    )

    print()
    print("Sentence:")
    print(result["sentence"])


    # ----------------------------------------------
    # Errors
    # ----------------------------------------------

    if result["errors"]:

        print()
        print("--- Grammar Problems ---")

        for error in result["errors"]:

            print(
                "❌",
                error
            )


        print()
        print("--- Suggestions ---")

        for suggestion in result["suggestions"]:

            print(
                "💡",
                suggestion
            )


        if result["corrections"]:

            print()
            print("--- Possible Corrections ---")

            for correction in result["corrections"]:

                print(
                    "→",
                    correction
                )

    else:

        print()
        print(
            "✅ No basic grammar problems detected."
        )


    # ----------------------------------------------
    # Summary
    # ----------------------------------------------

    print()
    print("--------------------------------")
    print(
        "Grammar errors:",
        result["error_count"]
    )
    print("--------------------------------")