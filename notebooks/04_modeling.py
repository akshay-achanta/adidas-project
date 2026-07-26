"""
PHASE 4: MODELING (the "AI" layer)
Location: notebooks/04_modeling.py
Input:  ../data/adidas_features.csv
Output: ../data/model.pkl  (used by the FastAPI backend in Phase 5)

Includes TWO models — pick the one that fits your goal, or keep both:
  A) Classification: predict Margin Bucket (Low/Medium/High) from Region, Product,
     Sales Method only — no Price/Units, so the model has to actually learn a
     business pattern instead of just recomputing arithmetic.
  B) Forecasting: predict next months' total sales (simple time-series regression)
"""

import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "../data/adidas_features.csv", parse_dates=["Invoice Date"])

# ---------- A) CLASSIFICATION: predict Margin Bucket ----------
# Deliberately EXCLUDING Price per Unit / Units Sold / Total Sales / Operating Profit —
# those directly determine margin, so including them would be leakage (see the
# R2=0.96 discussion). Only category context is given, so the model has to find
# a genuine pattern like "Outlet + Footwear tends to run High margin".
features = ["Region", "Product", "Sales Method"]
target = "Margin Bucket"

df = df.dropna(subset=[target])  # drop rows where bucket couldn't be computed
X = df[features]
y = df[target]

categorical = features  # all three are categorical

preprocessor = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
)

# NOTE: class_weight="balanced" was tested and improved Low-margin recall (13% -> 75%)
# but dropped overall CV accuracy to near-baseline (50.8%). Reverted to unbalanced
# since overall accuracy/stability was the priority for this report.
pipeline = Pipeline(steps=[
    ("preprocess", preprocessor),
    ("model", RandomForestClassifier(n_estimators=200, random_state=42)),
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
pipeline.fit(X_train, y_train)

preds = pipeline.predict(X_test)
acc = accuracy_score(y_test, preds)

print("=== Classification Model: Predict Margin Bucket (Low/Medium/High) ===")
print("Accuracy:", acc)
print("\nClassification report:\n", classification_report(y_test, preds))
print("Confusion matrix (rows=actual, cols=predicted):\n", confusion_matrix(y_test, preds))

# Baseline to compare against: what if we just always guessed the most common bucket?
baseline_acc = y_test.value_counts(normalize=True).max()
print(f"\nBaseline accuracy (always guess most common class): {baseline_acc:.1%}")
print(f"Model accuracy: {acc:.1%}")
print("If the model isn't clearly beating the baseline, Region/Product/Method")
print("alone may not carry enough signal — that's a real, honest finding too.")

# ---------- Cross-validation: more reliable than a single train/test split ----------
cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
print(f"\n5-fold Cross-Validated Accuracy scores: {cv_scores}")
print(f"Average CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

joblib.dump(pipeline, BASE_DIR / "../data/model.pkl")
print("\nSaved model to ../data/model.pkl")

# ---------- B) FORECASTING: monthly sales trend ----------
# Simple approach: turn month into a numeric index and fit a trend.
# For a stronger model, swap this for Prophet (pip install prophet).
monthly = df.groupby(df["Invoice Date"].dt.to_period("M"))["Total Sales"].sum().reset_index()
monthly["Invoice Date"] = monthly["Invoice Date"].astype(str)
monthly["month_index"] = range(len(monthly))

from sklearn.linear_model import LinearRegression

trend_model = LinearRegression()
trend_model.fit(monthly[["month_index"]], monthly["Total Sales"])

# Pass a DataFrame with the matching column name (not a bare list) to avoid the
# "X does not have valid feature names" warning.
next_index = pd.DataFrame({"month_index": [len(monthly)]})
forecast = trend_model.predict(next_index)
print("\n=== Forecast: Next Month's Total Sales ===")
print(f"Predicted: {forecast[0]:,.2f}")

joblib.dump(trend_model, BASE_DIR / "../data/trend_model.pkl")
print("Saved trend model to ../data/trend_model.pkl")