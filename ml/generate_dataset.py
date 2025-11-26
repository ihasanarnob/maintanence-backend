import pandas as pd
import numpy as np

# Number of samples
N = 300
np.random.seed(42)

# Define dataset
data = {
    "battery_health": np.random.randint(40, 101, N),
    "battery_cycles": np.random.randint(50, 600, N),
    "screen_on_time": np.random.randint(1, 10, N),  # hours/day
    "charging_frequency": np.random.randint(1, 4, N),
    "fast_charging": np.random.randint(0, 2, N),
    "charging_overnight": np.random.randint(0, 2, N),
    "overheating": np.random.randint(0, 2, N),
    "drop_history": np.random.randint(0, 3, N),  # 0=none,1=rare,2=frequent
    "water_damage": np.random.randint(0, 2, N),
    "sensor_issues": np.random.randint(0, 2, N),
    "battery_bulging": np.random.randint(0, 2, N),
    "screen_cracked": np.random.randint(0, 2, N),
    "buttons_not_working": np.random.randint(0, 2, N),
    "ram_usage": np.random.randint(30, 95, N),
    "storage_usage": np.random.randint(30, 95, N),
    "age_months": np.random.randint(3, 48, N),
    "overcharged": np.random.randint(0, 2, N),
}

df = pd.DataFrame(data)

# Generate label
def generate_label(row):
    if (
        row["battery_health"] < 60
        or row["overheating"]
        or row["battery_bulging"]
        or row["screen_cracked"]
        or row["water_damage"]
    ):
        return "critical"
    elif (
        row["battery_health"] < 80
        or row["drop_history"] > 0
        or row["ram_usage"] > 80
        or row["storage_usage"] > 80
    ):
        return "warning"
    else:
        return "healthy"

df["label"] = df.apply(generate_label, axis=1)

# Save to CSV
df.to_csv("ml/device_dataset.csv", index=False)
print("✅ Dataset saved to ml/device_dataset.csv")
print(df.head())
