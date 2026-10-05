FROM python:3.11-slim

# System deps for PDF/docx parsing + torch
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir requests

# Copy application code
COPY app/ ./app/
COPY data/ ./data/

# Hugging Face Spaces runs on port 7860
EXPOSE 7860

# Copy entrypoint script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]