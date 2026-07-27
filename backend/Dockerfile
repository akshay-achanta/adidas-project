FROM python:3.13-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py ./

# Copy the data files from the root data directory into the container's /app/data directory
COPY data/adidas_features.csv ./data/
COPY data/model.pkl ./data/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
