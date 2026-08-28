import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


# ==========================================
# 1. LOAD DATASET
# ==========================================

df = pd.read_csv(
    "data/in_domain_train.tsv",
    sep="\t",
    header=None,
    names=["source", "label", "annotation", "sentence"]
)

print("Dataset loaded successfully!")
print("Total sentences:", len(df))


# ==========================================
# 2. REMOVE EMPTY SENTENCES
# ==========================================

df = df.dropna(subset=["sentence", "label"])

print("Sentences after cleaning:", len(df))


# ==========================================
# 3. INPUT AND OUTPUT
# ==========================================

X = df["sentence"]
y = df["label"]


# ==========================================
# 4. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining sentences:", len(X_train))
print("Testing sentences:", len(X_test))


# ==========================================
# 5. CREATE ML PIPELINE
# ==========================================

model = Pipeline([
    
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        )
    )
])


# ==========================================
# 6. TRAIN MODEL
# ==========================================

print("\nTraining model...")

model.fit(X_train, y_train)

print("Training completed!")


# ==========================================
# 7. TEST MODEL
# ==========================================

y_pred = model.predict(X_test)


# ==========================================
# 8. MODEL PERFORMANCE
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

print("\n================================")
print("       MODEL PERFORMANCE")
print("================================")

print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Incorrect",
            "Correct"
        ]
    )
)


# ==========================================
# 9. TEST OUR OWN SENTENCES
# ==========================================

test_sentences = [

    "I am going to college.",

    "I am go to college.",

    "She is playing football.",

    "She are playing football.",

    "I have completed my homework.",

    "I has completed my homework.",

    "They are studying English.",

    "They is studying English.",

    "He went to the market yesterday.",

    "He go to the market yesterday."

]


# ==========================================
# 10. PREDICTIONS
# ==========================================

predictions = model.predict(test_sentences)


print("\n================================")
print("        SPEAKWISE TEST")
print("================================")


for sentence, prediction in zip(test_sentences, predictions):

    if prediction == 1:
        result = "Correct"
    else:
        result = "Incorrect"

    print(f"{sentence} → {result}")