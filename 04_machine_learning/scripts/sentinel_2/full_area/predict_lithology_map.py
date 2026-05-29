import rasterio
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

# -----------------------------
# Load training data
# -----------------------------

data = pd.read_csv(
    "/home/basti/Documents/Lund/Master_Thesis/03_processed/sampling/bedrock_study_area/training_samples.csv"
)

y = data["ML_Group"]
X = data.drop(columns=["ML_Group", "grid_id"])

# -----------------------------
# Train final Random Forest
# -----------------------------

rf = RandomForestClassifier(
    n_estimators=500, max_features="sqrt", random_state=42, n_jobs=-1
)

rf.fit(X, y)

print("Model trained.")

# -----------------------------
# Load predictor raster stack
# -----------------------------

raster_path = "/home/basti/Documents/Lund/Master_Thesis/03_processed/stacked/predictor_stacked_uncorrelated.tif"

with rasterio.open(raster_path) as src:
    profile = src.profile
    data_raster = src.read()

# shape = bands, rows, cols
bands, rows, cols = data_raster.shape

print("Raster shape:", data_raster.shape)

# -----------------------------
# Reshape raster for prediction
# -----------------------------

X_pred = data_raster.reshape(bands, -1).T

# replace NaNs
nan_mask = np.any(np.isnan(X_pred), axis=1)

X_valid = X_pred[~nan_mask]

# -----------------------------
# Predict classes
# -----------------------------

predictions = rf.predict(X_valid)

# create full prediction array
full_prediction = np.zeros(X_pred.shape[0])

full_prediction[~nan_mask] = predictions

# reshape to raster
prediction_map = full_prediction.reshape(rows, cols)

# -----------------------------
# Save output raster
# -----------------------------

profile.update(dtype=rasterio.uint16, count=1)

output_path = "/home/basti/Documents/Lund/Master_Thesis/03_processed/stacked/lithology_prediction_rf.tif"

with rasterio.open(output_path, "w", **profile) as dst:
    dst.write(prediction_map.astype(rasterio.uint16), 1)

print("Lithology map saved:", output_path)
