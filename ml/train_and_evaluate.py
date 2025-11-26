import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# === Load dataset ===
DATASET_PATH = "ml/device_dataset.csv"
MODEL_PATH = "ml/device_health_model.pkl"

df = pd.read_csv(DATASET_PATH)

# Feature columns (exclude label)
FEATURE_COLUMNS = [
    "battery_health","battery_cycles","screen_on_time","charging_frequency",
    "fast_charging","charging_overnight","overheating","drop_history","water_damage",
    "sensor_issues","battery_bulging","screen_cracked","buttons_not_working",
    "ram_usage","storage_usage","age_months","overcharged"
]

X = df[FEATURE_COLUMNS]
y = df["label"]

# === Split dataset (80% train, 20% test) ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# === Train model ===
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# === Save model (with feature metadata) ===
joblib.dump((model, FEATURE_COLUMNS), MODEL_PATH)
print(f"✅ Model trained and saved to {MODEL_PATH}")

# === Evaluate on test set ===
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
print("\n📊 Model Evaluation Results")
print("===========================")
print(f"Accuracy: {acc:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# === Feature Importance Visualization ===
importances = model.feature_importances_
feat_imp = pd.DataFrame({
    "Feature": FEATURE_COLUMNS,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(data=feat_imp, x="Importance", y="Feature", palette="viridis")
plt.title("🔍 Feature Importance in Device Health Prediction", fontsize=14)
plt.xlabel("Relative Importance")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig("ml/feature_importance.png")
plt.show()

print("\n📊 Feature importance plot saved as: ml/feature_importance.png")
