import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# ==========================================
# 1. LOAD DATASET
# ==========================================

df = pd.read_csv("data/fluency_data.csv")

print("Fluency dataset loaded!")
print("Total examples:", len(df))


# ==========================================
# 2. CREATE FEATURES
# ==========================================

# Import our feature extractor
from fluency import calculate_features


features = []

for sentence in df["sentence"]:

    result = calculate_features(sentence)

    features.append([
        result["word_count"],
        result["unique_words"],
        result["word_diversity"],
        result["avg_word_length"],
        result["sentence_complexity"]
    ])


X = pd.DataFrame(
    features,
    columns=[
        "word_count",
        "unique_words",
        "word_diversity",
        "avg_word_length",
        "sentence_complexity"
    ]
)

y = df["fluency_score"]


print("\nFeatures:")
print(X)


# ==========================================
# 3. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42
)


print("\nTraining examples:", len(X_train))
print("Testing examples:", len(X_test))


# ==========================================
# 4. CREATE ML MODEL
# ==========================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# ==========================================
# 5. TRAIN MODEL
# ==========================================

print("\nTraining fluency model...")

model.fit(X_train, y_train)

print("Training completed!")


# ==========================================
# 6. TEST MODEL
# ==========================================

predictions = model.predict(X_test)


# ==========================================
# 7. EVALUATE
# ==========================================

mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print("\n================================")
print("       FLUENCY MODEL")
print("================================")

print("MAE:", round(mae, 2))
print("R² Score:", round(r2, 2))


# ==========================================
# 8. TEST NEW SENTENCE
# ==========================================

sentence = input(
    "\nEnter a sentence to calculate fluency: "
)


result = calculate_features(sentence)


new_data = pd.DataFrame([[
    result["word_count"],
    result["unique_words"],
    result["word_diversity"],
    result["avg_word_length"],
    result["sentence_complexity"]
]], columns=X.columns)


score = model.predict(new_data)[0]


# Keep score between 0 and 100
score = max(0, min(100, score))


print("\n================================")
print("       SPEAKWISE RESULT")
print("================================")

print("Sentence:", sentence)

print(
    "Predicted Fluency:",
    round(score, 2),
    "/ 100"
)