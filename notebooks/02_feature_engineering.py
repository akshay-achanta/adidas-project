"""
PHASE 2: FEATURE ENGINEERING
Location: notebooks/02_feature_engineering.py
Input:  ../data/adidas_cleaned.csv   (output of Phase 1)
Output: ../data/adidas_features.csv (used by Phase 3 and 4)
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "../data/adidas_cleaned.csv", parse_dates=["Invoice Date"])

# Time-based features
df["Year"] = df["Invoice Date"].dt.year
df["Month"] = df["Invoice Date"].dt.to_period("M").astype(str)
df["Quarter"] = df["Invoice Date"].dt.to_period("Q").astype(str)
df["Weekday"] = df["Invoice Date"].dt.day_name()

# Efficiency features
df["Profit per Unit"] = df["Operating Profit"] / df["Units Sold"]
df["Revenue per Unit"] = df["Total Sales"] / df["Units Sold"]

# Simple margin bucket (useful later for classification model)
df["Margin Bucket"] = pd.cut(
    df["Operating Margin"],
    bins=[-1, 0.25, 0.40, 1],
    labels=["Low", "Medium", "High"],
)

print(df[["Invoice Date", "Month", "Quarter", "Profit per Unit", "Margin Bucket"]].head())

df.to_csv(BASE_DIR / "../data/adidas_features.csv", index=False)
print("\nSaved feature-engineered data to ../data/adidas_features.csv")