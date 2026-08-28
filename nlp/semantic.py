from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


print("Loading semantic NLP model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Model loaded successfully!")


def calculate_similarity(sentence1, sentence2):

    # Convert sentences into embeddings
    embedding1 = model.encode([sentence1])
    embedding2 = model.encode([sentence2])

    # Calculate similarity
    similarity = cosine_similarity(
        embedding1,
        embedding2
    )[0][0]

    return similarity


# ==========================================
# TEST
# ==========================================

sentence1 = input(
    "\nEnter first sentence: "
)

sentence2 = input(
    "Enter second sentence: "
)


score = calculate_similarity(
    sentence1,
    sentence2
)


print("\n================================")
print("       SEMANTIC ANALYSIS")
print("================================")

print("Sentence 1:")
print(sentence1)

print("\nSentence 2:")
print(sentence2)

print(
    "\nSemantic similarity:",
    round(score, 3)
)


if score >= 0.75:

    print("Meaning: Very similar 🟢")

elif score >= 0.50:

    print("Meaning: Somewhat similar 🟡")

else:

    print("Meaning: Different 🔴")