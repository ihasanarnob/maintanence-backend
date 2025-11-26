# train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

# Load dataset
DATA_PATH = "ml/device_dataset.csv"
df = pd.read_csv(DATA_PATH)

# Feature columns (all inputs except the label)
FEATURE_COLUMNS = [
    "battery_health","battery_cycles","screen_on_time","charging_frequency",
    "fast_charging","charging_overnight","overheating","drop_history","water_damage",
    "sensor_issues","battery_bulging","screen_cracked","buttons_not_working",
    "ram_usage","storage_usage","age_months","overcharged"
]

X = df[FEATURE_COLUMNS]
y = df["label"]

# Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train RandomForest model
model = RandomForestClassifier(n_estimators=150, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Save model and feature order
MODEL_DIR = "ml"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "device_health_model.pkl")
joblib.dump((model, FEATURE_COLUMNS), MODEL_PATH)

print(f"\n✅ Model saved to {MODEL_PATH}")
