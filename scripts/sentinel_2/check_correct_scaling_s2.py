import os
import rasterio
import numpy as np


tile_folder = r"home/basti/Documents/Lund/Master_Thesis/02_raw_data"

# Thresholds (adjust if needed)
upper_threshold = 1.5
lower_threshold = -0.01

print(f"\nChecking tiles in: {tile_folder}\n")

# -------------------------
# LOOP OVER TILES
# -------------------------

for file in os.listdir(tile_folder):

    if not file.endswith(".tif"):
        continue

    path = os.path.join(tile_folder, file)

    with rasterio.open(path) as src:
        data = src.read()  # shape: (bands, height, width)

    # Flatten ignoring NaNs
    flat = data.flatten()
    flat = flat[~np.isnan(flat)]

    if flat.size == 0:
        print(f"{file} → ALL VALUES ARE NaN")
        continue

    min_val = np.min(flat)
    max_val = np.max(flat)
    mean_val = np.mean(flat)
    p99 = np.percentile(flat, 99)

    flag = ""

    if max_val > upper_threshold:
        flag += "  ⚠ HIGH OUTLIER"

    if min_val < lower_threshold:
        flag += "  ⚠ NEGATIVE OUTLIER"

    print(f"{file}")
    print(f"  Min: {min_val:.4f}")
    print(f"  Max: {max_val:.4f}")
    print(f"  Mean: {mean_val:.4f}")
    print(f"  99th percentile: {p99:.4f}")
    print(flag)
    print("-" * 40)

print("\nDone.")