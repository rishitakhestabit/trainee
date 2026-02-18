import csv
import json
import os
import time
from datetime import datetime
from uuid import uuid4
from typing import Any, Dict

from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator


# -----------------------
# Config
# -----------------------
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")

# Full inference pipeline (feature_eng + preprocess + model)
PIPELINE_PATH = os.getenv(
    "INFERENCE_PIPELINE_PATH",
    f"src/models/inference_pipeline_{MODEL_VERSION}.joblib"
)

# Log at Week6 root
BASE_DIR = Path(__file__).resolve().parents[2]
LOG_PATH = os.getenv("PREDICTION_LOG_PATH", str(BASE_DIR / "prediction_logs.csv"))
Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Churn Prediction API", version=MODEL_VERSION)

PIPELINE = None

LOG_FIELDS = [
    "timestamp",
    "request_id",
    "model_version",
    "latency_ms",
    "prediction",
    "prediction_label",
    "probability",
    "true_label",
    "is_correct",
    "label_timestamp",
    "input_json",
]


# -----------------------
# Request schema
# -----------------------
class PredictPayload(BaseModel):
    features: Dict[str, Any] = Field(..., description="Raw input features as key-value pairs")

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: Dict[str, Any]):
        if not isinstance(v, dict) or len(v) == 0:
            raise ValueError("features must be a non-empty object")
        for k, val in v.items():
            if isinstance(val, (dict, list)):
                raise ValueError(f"Invalid value type for '{k}': nested objects/lists not allowed")
        return v


class FeedbackPayload(BaseModel):
    request_id: str = Field(..., description="request_id received from /predict response")
    true_label: int = Field(..., ge=0, le=1, description="0 = No churn, 1 = Churn")


# -----------------------
# Middleware: Request ID
# -----------------------
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# -----------------------
# Load pipeline on startup
# -----------------------
@app.on_event("startup")
def load_pipeline():
    global PIPELINE

    if not os.path.exists(PIPELINE_PATH):
        raise FileNotFoundError(
            f"Inference pipeline not found at {PIPELINE_PATH}. "
            f"Run Day-3/Day-4 training to generate it."
        )

    PIPELINE = joblib.load(PIPELINE_PATH)
    print(f"[OK] Loaded pipeline: {PIPELINE_PATH}")
    print(f"[OK] Model version: {MODEL_VERSION}")


# -----------------------
# Helpers: logging
# -----------------------
def ensure_log_header(path: str):
    if os.path.exists(path):
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writeheader()


def append_prediction_log(row: Dict[str, Any], path: str):
    ensure_log_header(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writerow(row)


def to_dataframe(features: Dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame([features])


def predict_with_pipeline(df: pd.DataFrame):
    pred = PIPELINE.predict(df)
    pred_label = int(pred[0]) if hasattr(pred, "__len__") else int(pred)

    proba = None
    # Pipeline should expose predict_proba if final estimator does
    if hasattr(PIPELINE, "predict_proba"):
        proba = float(PIPELINE.predict_proba(df)[:, 1][0])

    return pred_label, proba


def update_feedback_in_log(path: str, target_request_id: str, true_label: int):
    """
    Update a row in prediction_logs.csv matching request_id with true_label,
    then compute is_correct.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Log file not found: {path}")

    df = pd.read_csv(path)

    if "request_id" not in df.columns:
        raise ValueError("prediction_logs.csv missing 'request_id' column")

    mask = df["request_id"].astype(str) == str(target_request_id)
    if mask.sum() == 0:
        raise ValueError(f"request_id not found: {target_request_id}")

    # Update first matched row
    idx = df.index[mask][0]

    pred = df.loc[idx, "prediction"]
    if pd.isna(pred) or str(pred).strip() == "":
        raise ValueError(f"Missing prediction for request_id: {target_request_id}")

    pred = int(pred)
    true_label = int(true_label)

    df.loc[idx, "true_label"] = true_label
    df.loc[idx, "is_correct"] = int(pred == true_label)
    df.loc[idx, "label_timestamp"] = datetime.utcnow().isoformat()

    df.to_csv(path, index=False)


# -----------------------
# Routes
# -----------------------
@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/predict")
def predict(payload: PredictPayload, request: Request):
    start = time.time()
    request_id = getattr(request.state, "request_id", str(uuid4()))

    try:
        df = to_dataframe(payload.features)
        pred_label, proba = predict_with_pipeline(df)

        latency_ms = round((time.time() - start) * 1000, 2)

        # readable label
        prediction_label = "Yes" if pred_label == 1 else "No"  # Yes = churn

        log_row = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "model_version": MODEL_VERSION,
            "latency_ms": latency_ms,
            "prediction": pred_label,
            "prediction_label": prediction_label,
            "probability": proba if proba is not None else "",
            "true_label": "",
            "is_correct": "",
            "label_timestamp": "",
            "input_json": json.dumps(payload.features),
        }
        append_prediction_log(log_row, LOG_PATH)

        return {
            "request_id": request_id,
            "model_version": MODEL_VERSION,
            "prediction": pred_label,
            "prediction_label": prediction_label,
            "probability": proba,
            "latency_ms": latency_ms,
        }

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"request_id": request_id, "error": str(e)},
        )


@app.post("/feedback")
def feedback(payload: FeedbackPayload, request: Request):
    """
    Delayed label endpoint.
    Use this when you later know if churn actually happened.
    """
    req_id = getattr(request.state, "request_id", str(uuid4()))
    try:
        update_feedback_in_log(LOG_PATH, payload.request_id, payload.true_label)
        return {
            "request_id": req_id,
            "status": "ok",
            "updated_request_id": payload.request_id,
            "true_label": payload.true_label,
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"request_id": req_id, "error": str(e)},
        )
