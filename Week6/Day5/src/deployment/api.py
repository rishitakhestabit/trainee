import uuid
import json
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import os

app = FastAPI(title="House Price Classifier", version="1.0")

MODEL_PATH = "./src/models/best_model.pkl"
FEATURES_PATH = "./src/features/feature_list.json"
LOG_PATH = "prediction_logs.csv"

model = joblib.load(MODEL_PATH)

with open(FEATURES_PATH) as f:
    FEATURE_COLUMNS = json.load(f)

class PredictionRequest(BaseModel):
    longitude: float = Field(..., example=-122.23)
    latitude: float = Field(..., example=37.88)
    housing_median_age: float = Field(..., example=41.0)
    total_rooms: float = Field(..., example=880.0)
    total_bedrooms: float = Field(..., example=129.0)
    population: float = Field(..., example=322.0)
    households: float = Field(..., example=126.0)
    median_income: float = Field(..., example=1.23)

def transform_input(payload: dict) -> np.ndarray:
    df = pd.DataFrame([payload])
    
    df["rooms_per_hh"] = df["total_rooms"] / df["households"]
    df["bed_per_room"] = df["total_bedrooms"] / df["total_rooms"]
    df["pop_per_hh"] = df["population"] / df["households"]
    df["log_income"] = np.log1p(df["median_income"])
    
    df = df.reindex(columns=FEATURE_COLUMNS, fill_value=0)
    
    return df.values

def log_prediction(request_id, payload, prediction, probability):
    log_row = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "prediction": prediction,
        "probability": probability,
        **payload
    }
    
    df_log = pd.DataFrame([log_row])
    
    if not os.path.exists(LOG_PATH):
        df_log.to_csv(LOG_PATH, index=False)
    else:
        df_log.to_csv(LOG_PATH, mode="a", header=False, index=False)

@app.get("/")
def health():
    return {"status": "API is running"}

@app.post("/predict")
def predict(request: PredictionRequest):
    request_id = str(uuid.uuid4())
    
    payload = request.dict()
    X = transform_input(payload)
    
    proba = model.predict_proba(X)[0][1]
    probability = float(proba)
    prediction = int(probability >= 0.5)
    
    log_prediction(request_id, payload, prediction, probability)
    
    return {
        "request_id": request_id,
        "prediction": prediction,
        "probability": probability
    }

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}
