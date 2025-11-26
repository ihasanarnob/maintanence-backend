# main/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PredictiveMaintenance
import joblib
import os

# Load the ML model and feature columns once
MODEL_PATH = os.path.join("ml", "device_health_model.pkl")
model, FEATURE_COLUMNS = joblib.load(MODEL_PATH)

@receiver(post_save, sender=PredictiveMaintenance)
def run_ml_prediction(sender, instance, created, **kwargs):
    """
    Run ML prediction when a PredictiveMaintenance record is saved.
    Only uses ML-relevant fields and fills missing values with 0.
    """
    # Gather features in the correct order, fill missing with 0
    data = instance.__dict__
    features = []
    for col in FEATURE_COLUMNS:
        val = data.get(col, 0)
        # Convert any string that can be numeric to float, else keep 0
        if isinstance(val, str):
            try:
                val = float(val)
            except ValueError:
                val = 0
        features.append(val)

    # Predict
    try:
        prediction = model.predict([features])[0]
    except Exception as e:
        print(f"ML prediction error: {e}")
        return

    # Update instance only if prediction changed
    if instance.ml_prediction != prediction:
        # Avoid recursion by updating fields directly
        PredictiveMaintenance.objects.filter(id=instance.id).update(ml_prediction=prediction)
