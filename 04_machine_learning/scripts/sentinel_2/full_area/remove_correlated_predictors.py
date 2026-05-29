import numpy as np
import rasterio
import yaml
import os

"""
This script harmonizes NaNs across bands and
removes highly correlated predictors from the stacked raster.
"""


with open(
    r"/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml",
    "r",
) as f:
    config = yaml.safe_load(f)

input_raster = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "stacked",
    "predictor_stacked.tif",
)

output_raster = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "stacked",
    "predictor_stacked_uncorrelated.tif",
)

threshold = 0.9

with rasterio.open(input_raster) as src:
    data = src.read().astype("float32")  # (bands, rows, cols)
    profile = src.profile.copy()


# 1. harmonize NaNs across bands. If any band is NaN at a pixel, set all bands to NaN at that pixel.
# Find pixels where band is NaN
invalid_mask = np.isnan(data).any(axis=0)

# Set bands to NaN at those pixels
data[:, invalid_mask] = np.nan


# 2. remove highly correlated predictors from the stacked raster
# reshape to (pixels, bands) for correlation analysis (e.g. (9, 100, 100) -> (9, 10000))
bands, rows, cols = data.shape
X = data.reshape(bands, -1).T

# correlation matrix can't handle NaNs
valid = ~np.isnan(X).any(axis=1)
X_valid = X[valid]

# numpy correlation matrix
corr_matrix = np.corrcoef(X_valid, rowvar=False)

print("\nCorrelation matrix:\n", corr_matrix)


# find predictors to drop based on correlation threshold
to_drop = set()

for i in range(corr_matrix.shape[0]):
    for j in range(i):
        if abs(corr_matrix[i, j]) >= threshold:
            to_drop.add(i)

keep = [i for i in range(bands) if i not in to_drop]

print("\nPredictors kept:", keep)
print("Predictors removed:", list(to_drop))


# create reduced stack with only uncorrelated predictors
reduced = data[keep, :, :]


profile.update(count=len(keep), dtype="float32", nodata=np.nan)

with rasterio.open(output_raster, "w", **profile) as dst:
    dst.write(reduced)

print("\nSaved reduced predictor stack:", output_raster)
