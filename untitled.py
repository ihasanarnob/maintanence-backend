import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load your dataset
data = pd.read_csv("ml/device_data.csv")

# Train a simple model
X = data.drop("label", axis=1)
y = data["label"]
model = RandomForestClassifier()
model.fit(X, y)

# Save the trained model
joblib.dump((model, list(X.columns)), "ml/device_health_model.pkl")


