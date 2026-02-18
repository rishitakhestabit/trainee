# DEPLOYMENT NOTES --- Day 5 (Model Deployment & Monitoring)

## Overview

Day 5 focuses on converting the trained churn prediction model into a
production-style machine learning service. The goal is not improving
accuracy --- it is making the model usable, observable and reliable.

We implemented: - FastAPI serving - Inference pipeline loading - Request
validation - Prediction logging - Request ID tracking - Data drift
monitoring - Accuracy decay monitoring - Docker deployment


## Inference Pipeline

Instead of deploying only the trained model, a full pipeline artifact
was saved:

Feature Engineering -> Encoding -> Scaling -> Model

File: src/models/inference_pipeline_v1.joblib

This ensures training and prediction follow identical transformations
and prevents training‑serving skew.


## FastAPI Serving

Server command:

uvicorn src.deployment.api:app --reload

Endpoint: POST /predict

Flow: 1. Receive JSON features 2. Validate schema 3. Convert JSON →
DataFrame 4. Run pipeline.predict() 5. Return prediction + probability
6. Log request



## Request Tracking

Every request generates an X‑Request‑ID. This helps trace errors and
reproduce specific predictions.


## Prediction Logging

All predictions are stored in:

prediction_logs.csv

Stored fields: timestamp, request_id, model_version, latency_ms,
prediction, probability, input_json

This allows monitoring and debugging.



## Data Drift Monitoring

Command: python -m src.monitoring.drift_checker

Compares production data vs training data using PSI (Population
Stability Index).

Interpretation: PSI \< 0.1 → stable 0.1--0.2 → warning \> 0.2 → drift
detected

Output: src/monitoring/drift_report.json


## Accuracy Monitoring

Command: python -m src.monitoring.accuracy_monitor

Compares predictions with true labels once feedback is available.
Detects model degradation over time.

Output: src/monitoring/accuracy_report.json



## Docker Deployment

Build: docker build -t churn-api .

Run: docker run -p 8000:8000 churn-api

The model now runs independently of local environment.


## Final Result

The ML model is now: Deployable, reproducible, observable and
monitorable --- similar to real production ML systems.
