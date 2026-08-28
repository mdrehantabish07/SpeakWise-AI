import re

from wordfreq import zipf_frequency


def analyze_vocabulary(sentence):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        sentence.lower()
    )

    results = []

    for word in words:

        frequency = zipf_frequency(
            word,
            "en"
        )

        if frequency == 0:

            status = "Suspicious"

        elif frequency < 2:

            status = "Uncommon"

        else:

            status = "Common"

        results.append({
            "word": word,
            "frequency": round(frequency, 2),
            "status": status
        })

    return results


# =====================================
# TEST
# =====================================

sentence = input(
    "Enter an English sentence: "
)

results = analyze_vocabulary(sentence)


print("\n================================")
print("     VOCABULARY ANALYSIS")
print("================================")


for item in results:

    print(
        f"{item['word']:15} "
        f"{item['frequency']:5} "
        f"{item['status']}"
    )