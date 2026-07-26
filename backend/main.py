"""
PHASE 5: FASTAPI BACKEND
Location: backend/main.py
Run with: uvicorn main:app --reload   (from inside backend/)
Serves cleaned data summaries + model predictions as JSON for the React frontend.

Expects ../data/adidas_features.csv and ../data/model.pkl to already exist
(i.e. run Phases 1-4 first).
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import pandas as pd
import joblib

app = FastAPI(title="Adidas Sales API")

BASE_DIR = Path(__file__).resolve().parent
candidate_dirs = [
    BASE_DIR / "data",
    BASE_DIR.parent / "data",
    Path("/app/data"),
    Path("/data"),
]

DATA_DIR = None
DATA_FILE = None
MODEL_FILE = None

for candidate_dir in candidate_dirs:
    candidate_data = candidate_dir / "adidas_features.csv"
    candidate_model = candidate_dir / "model.pkl"
    if candidate_data.exists() and candidate_model.exists():
        DATA_DIR = candidate_dir
        DATA_FILE = candidate_data
        MODEL_FILE = candidate_model
        break

if DATA_DIR is None or DATA_FILE is None or MODEL_FILE is None:
    raise FileNotFoundError(
        "Expected data/model files in one of: "
        f"{candidate_dirs[0]}, {candidate_dirs[1]}, {candidate_dirs[2]}, {candidate_dirs[3]}"
    )

# Allow the React dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv(DATA_FILE, parse_dates=["Invoice Date"])
model = joblib.load(MODEL_FILE)


def apply_filters(
    data: pd.DataFrame,
    region: Optional[str] = None,
    sales_method: Optional[str] = None,
    product: Optional[str] = None,
) -> pd.DataFrame:
    """Shared cross-filter logic. Any of these can be passed as query params
    from the frontend (e.g. ?region=Northeast) to narrow every endpoint down
    to a consistent slice of the data."""
    if region:
        data = data[data["Region"] == region]
    if sales_method:
        data = data[data["Sales Method"] == sales_method]
    if product:
        data = data[data["Product"] == product]
    return data


@app.get("/")
def root():
    return {"status": "ok", "rows": len(df)}


@app.get("/data/summary")
def summary(
    region: Optional[str] = None,
    sales_method: Optional[str] = None,
    product: Optional[str] = None,
):
    filtered = apply_filters(df, region, sales_method, product)
    if len(filtered) == 0:
        return {"total_sales": 0, "total_profit": 0, "avg_margin": 0, "total_units": 0}
    return {
        "total_sales": float(filtered["Total Sales"].sum()),
        "total_profit": float(filtered["Operating Profit"].sum()),
        "avg_margin": float(filtered["Operating Margin"].mean()),
        "total_units": int(filtered["Units Sold"].sum()),
    }


@app.get("/data/trends")
def trends(
    region: Optional[str] = None,
    sales_method: Optional[str] = None,
    product: Optional[str] = None,
):
    filtered = apply_filters(df, region, sales_method, product)
    monthly = (
        filtered.groupby(filtered["Invoice Date"].dt.to_period("M"))["Total Sales"]
        .sum()
        .reset_index()
    )
    monthly["Invoice Date"] = monthly["Invoice Date"].astype(str)
    return monthly.to_dict(orient="records")


@app.get("/data/by-region")
def by_region(
    sales_method: Optional[str] = None,
    product: Optional[str] = None,
):
    # Note: no 'region' param here on purpose — this chart always shows the
    # full region breakdown so you always have something to click on.
    # It still respects sales_method/product filters from OTHER charts.
    filtered = apply_filters(df, None, sales_method, product)
    result = filtered.groupby("Region")["Operating Profit"].sum().reset_index()
    return result.to_dict(orient="records")


@app.get("/data/by-sales-method")
def by_sales_method(
    region: Optional[str] = None,
    product: Optional[str] = None,
):
    filtered = apply_filters(df, region, None, product)
    result = filtered.groupby("Sales Method")["Operating Margin"].mean().reset_index()
    return result.to_dict(orient="records")


@app.get("/data/top-products")
def top_products(
    region: Optional[str] = None,
    sales_method: Optional[str] = None,
):
    filtered = apply_filters(df, region, sales_method, None)
    result = (
        filtered.groupby("Product")["Total Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    return result.to_dict(orient="records")


class PredictionInput(BaseModel):
    region: str
    product: str
    sales_method: str


@app.post("/predict")
def predict(payload: PredictionInput):
    input_df = pd.DataFrame([{
        "Region": payload.region,
        "Product": payload.product,
        "Sales Method": payload.sales_method,
    }])
    predicted_bucket = model.predict(input_df)[0]
    probabilities = dict(zip(model.classes_, model.predict_proba(input_df)[0]))
    return {
        "predicted_margin_bucket": predicted_bucket,
        "probabilities": {k: float(v) for k, v in probabilities.items()},
    }