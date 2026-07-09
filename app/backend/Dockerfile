FROM python:3.11-slim

WORKDIR /app

# System deps needed for pdfplumber / OCR later on
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ara \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt now lives at the repo root, not inside app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy just the backend source code
COPY app/backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]