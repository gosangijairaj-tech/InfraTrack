import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib

# Load dataset
df = pd.read_csv("data.csv")

# Input
X = df["description"]

# Outputs
y_category = df["category"]
y_score = df["risk_score"]

# Convert text → numbers
vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

# Train models
cat_model = RandomForestClassifier()
cat_model.fit(X_vec, y_category)

score_model = RandomForestRegressor()
score_model.fit(X_vec, y_score)

# Save models
joblib.dump(vectorizer, "vectorizer.pkl")
joblib.dump(cat_model, "cat_model.pkl")
joblib.dump(score_model, "score_model.pkl")

print("✅ Training complete!")