"""
PHASE 3: EXPLORATORY DATA ANALYSIS (EDA)
Location: notebooks/03_eda.py
Input:  ../data/adidas_features.csv (output of Phase 2)
Output: PNG charts in ../data/charts/ + a printed findings summary
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CHARTS_DIR = BASE_DIR / "../data/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)
sns.set_style("whitegrid")

df = pd.read_csv(BASE_DIR / "../data/adidas_features.csv", parse_dates=["Invoice Date"])

# 1. Monthly sales trend
monthly = df.groupby("Month")["Total Sales"].sum().reset_index()
plt.figure(figsize=(10, 4))
sns.lineplot(data=monthly, x="Month", y="Total Sales", marker="o")
plt.xticks(rotation=45)
plt.title("Monthly Total Sales")
plt.tight_layout()
plt.savefig(str(CHARTS_DIR) + "/01_monthly_sales_trend.png")
plt.close()

# 2. Profit by region
region_profit = df.groupby("Region")["Operating Profit"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 4))
sns.barplot(x=region_profit.index, y=region_profit.values)
plt.title("Operating Profit by Region")
plt.tight_layout()
plt.savefig(str(CHARTS_DIR) + "/02_profit_by_region.png")
plt.close()

# 3. Avg margin by sales method
method_margin = df.groupby("Sales Method")["Operating Margin"].mean().sort_values(ascending=False)
plt.figure(figsize=(6, 4))
sns.barplot(x=method_margin.index, y=method_margin.values)
plt.title("Avg Operating Margin by Sales Method")
plt.tight_layout()
plt.savefig(str(CHARTS_DIR) + "/03_margin_by_sales_method.png")
plt.close()

# 4. Top products by total sales
top_products = df.groupby("Product")["Total Sales"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(8, 5))
sns.barplot(x=top_products.values, y=top_products.index)
plt.title("Top 10 Products by Total Sales")
plt.tight_layout()
plt.savefig(str(CHARTS_DIR) + "/04_top_products.png")
plt.close()

# 5. Price vs Units Sold (elasticity intuition)
plt.figure(figsize=(6, 5))
sns.scatterplot(data=df, x="Price per Unit", y="Units Sold", alpha=0.4)
plt.title("Price per Unit vs Units Sold")
plt.tight_layout()
plt.savefig(str(CHARTS_DIR) + "/05_price_vs_units.png")
plt.close()

# 6. Correlation heatmap
numeric_cols = ["Price per Unit", "Units Sold", "Total Sales", "Operating Profit", "Operating Margin"]
plt.figure(figsize=(6, 5))
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(str(CHARTS_DIR) + "/06_correlation_heatmap.png")
plt.close()

# ---- Printed findings summary (fill these in after you look at the charts) ----
print("=== QUICK FINDINGS ===")
print("Best region by profit:", region_profit.idxmax())
print("Best sales method by margin:", method_margin.idxmax(), f"({method_margin.max():.1%})")
print("Top product:", top_products.idxmax())
print("\nCharts saved in ../data/charts/")