# train_model.py (put this beside manage.py)
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# ---- 1) Make synthetic/fake but realistic data ----
np.random.seed(42)
n = 2000
df = pd.DataFrame({
    "battery_health": np.random.randint(40, 101, n),    # %
    "storage_usage":  np.random.randint(30, 100, n),    # %
    "ram_usage":      np.random.randint(30, 100, n),    # %
    "overheating":    np.random.randint(0, 2, n),       # 0/1
    "drop_history":   np.random.randint(0, 2, n),       # 0/1
    "water_damage":   np.random.randint(0, 2, n),       # 0/1
    "sensor_issues":  np.random.randint(0, 2, n),       # 0/1
    "battery_bulging":np.random.randint(0, 2, n),       # 0/1
    "screen_cracked": np.random.randint(0, 2, n),       # 0/1
    "buttons_not_working": np.random.randint(0, 2, n),  # 0/1
})

# Rule-of-thumb risk score to label the data (you can tweak anytime)
scores = []
for _, r in df.iterrows():
    s = 0
    s += 2 if r["battery_health"] < 55 else (1 if r["battery_health"] < 65 else 0)
    s += 1 if r["storage_usage"]  > 85 else 0
    s += 1 if r["ram_usage"]      > 85 else 0
    s += 2 * r["overheating"]
    s += 1 * r["drop_history"]
    s += 2 * r["water_damage"]
    s += 1 * r["sensor_issues"]
    s += 2 * r["battery_bulging"]
    s += 1 * r["screen_cracked"]
    s += 1 * r["buttons_not_working"]
    scores.append(s)

labels = []
for s in scores:
    if s <= 2:   labels.append(0)  # Healthy
    elif s <=5:  labels.append(1)  # Warning
    else:        labels.append(2)  # Critical

df["failure_risk"] = labels

# ---- 2) Train a model ----
X = df.drop(columns=["failure_risk"])
y = df["failure_risk"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=300, random_state=42)
model.fit(X_train, y_train)
acc = model.score(X_test, y_test)
print(f"✅ Model trained. Test accuracy: {acc:.2f}")

# ---- 3) Save model into the Django app folder: main/predictive_model.pkl ----
dest_dir = os.path.join(os.path.dirname(__file__), "main")
os.makedirs(dest_dir, exist_ok=True)
dest_path = os.path.join(dest_dir, "predictive_model.pkl")

joblib.dump(model, dest_path)
print(f"💾 Saved model → {dest_path}")
