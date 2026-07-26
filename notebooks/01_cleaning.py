"""
PHASE 1: DATA CLEANING
Run this first.

Input:
    data/adidas_sales.xlsx

Output:
    data/adidas_cleaned.csv
"""

import pandas as pd
from pathlib import Path

# ============================
# Paths
# ============================
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "adidas_sales.csv"
OUTPUT_PATH = BASE_DIR / "data" / "adidas_cleaned.csv"


df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

# Remove extra spaces from column names
df.columns = df.columns.str.strip()

print("=" * 50)
print("Dataset Loaded Successfully")
print("=" * 50)

print("\nShape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:", df.duplicated().sum())


# ============================
# Cleaning Functions
# ============================

def clean_money(series):
    """
    Converts:
    $6,00,000 -> 600000
    """

    return (
        series.astype(str)
        .str.replace(r"[\$,]", "", regex=True)
        .str.strip()
        .replace("", None)
        .astype(float)
    )


def clean_number(series):
    """
    Converts:
    1,200 -> 1200
    """

    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("", None)
        .astype(float)
        .astype(int)
    )


def clean_percent(series):
    """
    Converts:
    50% -> 0.50
    """

    return (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace("", None)
        .astype(float)
        / 100
    )


# ============================
# Clean Numeric Columns
# ============================

money_columns = [
    "Price per Unit",
    "Total Sales",
    "Operating Profit"
]

for column in money_columns:
    df[column] = clean_money(df[column])

df["Units Sold"] = clean_number(df["Units Sold"])

df["Operating Margin"] = clean_percent(df["Operating Margin"])


# ============================
# Date Column
# ============================

df["Invoice Date"] = pd.to_datetime(
    df["Invoice Date"],
    dayfirst=True,
    errors="coerce"
)


# ============================
# Text Columns
# ============================

text_columns = [
    "Retailer",
    "Region",
    "State",
    "City",
    "Product",
    "Sales Method"
]

for column in text_columns:
    df[column] = df[column].astype(str).str.strip()


# ============================
# Remove Duplicates
# ============================

df.drop_duplicates(inplace=True)


# ============================
# Remove Invalid Rows
# ============================

df.dropna(
    subset=[
        "Invoice Date",
        "Total Sales",
        "Units Sold"
    ],
    inplace=True
)


# ============================
# Reset Index
# ============================

df.reset_index(drop=True, inplace=True)


print("\n")
print("=" * 50)
print("After Cleaning")
print("=" * 50)

print("\nShape:", df.shape)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nData Types:")
print(df.dtypes)

print("\nFirst 5 Rows:")
print(df.head())


# ============================
# Save Cleaned Dataset
# ============================

df.to_csv(OUTPUT_PATH, index=False)

print("\n")
print("=" * 50)
print("Cleaning Completed Successfully")
print("=" * 50)
print(f"Saved to:\n{OUTPUT_PATH}")