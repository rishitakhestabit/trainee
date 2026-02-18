FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV MODEL_VERSION=v1
ENV INFERENCE_PIPELINE_PATH=src/models/inference_pipeline_v1.joblib
ENV PREDICTION_LOG_PATH=/app/prediction_logs.csv
ENV REFERENCE_DATA_PATH=/app/src/data/processed/final.csv

EXPOSE 8000

CMD ["uvicorn", "src.deployment.api:app", "--host", "0.0.0.0", "--port", "8000"]
