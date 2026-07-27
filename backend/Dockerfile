FROM python:3.13-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/*.py ./

# Copy essential data files for application startup
COPY data/adidas_features.csv ./data/
COPY data/model.pkl ./data/
COPY data/trend_model.pkl ./data/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
