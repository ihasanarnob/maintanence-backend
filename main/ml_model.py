# main/ml_model.py
import os
import joblib
import numpy as np

# Lazy global cache so Django doesn’t reload the model repeatedly
_MODEL = None
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "predictive_model.pkl")
_LABELS = {0: "Healthy", 1: "Warning", 2: "Critical"}

def _load_model():
    global _MODEL
    if _MODEL is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at {_MODEL_PATH}. "
                "Train it with train_model.py and ensure it’s placed here."
            )
        _MODEL = joblib.load(_MODEL_PATH)
    return _MODEL

# The exact order of features the model expects
_FEATURE_ORDER = [
    "battery_health",
    "storage_usage",
    "ram_usage",
    "overheating",
    "drop_history",
    "water_damage",
    "sensor_issues",
    "battery_bulging",
    "screen_cracked",
    "buttons_not_working",
]

def _coerce(x, default=0):
    # Safely coerce booleans/strings to numbers (0/1 or ints)
    if isinstance(x, bool): return int(x)
    try:
        return int(x)
    except Exception:
        try:
            return float(x)
        except Exception:
            return default

def predict_failure(payload: dict):
    """
    payload is a dict with keys matching _FEATURE_ORDER.
    Missing fields are filled with reasonable defaults.
    Returns: dict with label, class, probabilities
    """
    model = _load_model()

    row = []
    for f in _FEATURE_ORDER:
        val = payload.get(f, 0)
        row.append(_coerce(val, 0))
    X = np.array([row])

    pred_class = int(model.predict(X)[0])
    # If model doesn’t support predict_proba, make a safe fallback
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0].tolist()
    else:
        proba = [0, 0, 0]
        proba[pred_class] = 1.0

    return {
        "label": _LABELS.get(pred_class, str(pred_class)),
        "class": pred_class,
        "probabilities": proba
    }
