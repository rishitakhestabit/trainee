# Use Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for llama-cpp)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (create if not present)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Create logs folder (your app needs this)
RUN mkdir -p logs

# Expose API port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "deploy.app:app", "--host", "0.0.0.0", "--port", "8000"]