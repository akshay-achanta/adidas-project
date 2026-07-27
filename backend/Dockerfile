FROM python:3.13-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/*.py ./

# Copy essential data files for the model to load
RUN mkdir -p ./data
COPY data/adidas_features.csv ./data/adidas_features.csv
COPY data/model.pkl ./data/model.pkl

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
