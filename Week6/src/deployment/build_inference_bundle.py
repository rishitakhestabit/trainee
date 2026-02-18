import json
import os
import joblib

BEST_MODEL_PATH = "src/models/best_model.pkl"
PREPROCESSOR_PATH = "src/features/preprocessor.joblib"
FEATURE_LIST_PATH = "src/features/feature_list.json"

OUT_DIR = "src/models"
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")
OUT_PATH = os.path.join(OUT_DIR, f"inference_bundle_{MODEL_VERSION}.joblib")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(BEST_MODEL_PATH):
        raise FileNotFoundError(f"Missing model: {BEST_MODEL_PATH}")
    if not os.path.exists(PREPROCESSOR_PATH):
        raise FileNotFoundError(f"Missing preprocessor: {PREPROCESSOR_PATH}")
    if not os.path.exists(FEATURE_LIST_PATH):
        raise FileNotFoundError(f"Missing feature list: {FEATURE_LIST_PATH}")

    model = joblib.load(BEST_MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)

    with open(FEATURE_LIST_PATH, "r") as f:
        feature_list = json.load(f)

    bundle = {
        "model_version": MODEL_VERSION,
        "model": model,
        "preprocessor": preprocessor,
        "feature_list": feature_list,
    }

    joblib.dump(bundle, OUT_PATH)
    print(f"[OK] Saved inference bundle: {OUT_PATH}")


if __name__ == "__main__":
    main()
