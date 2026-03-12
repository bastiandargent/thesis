import os
import numpy as np
import rasterio

root = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/merge"
out = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/composite"

os.makedirs(out, exist_ok=True)

years = [2022, 2023, 2024, 2025]

arrays = []

for year in years:
    path = os.path.join(root, f"{year}_mosaic.tif")

    with rasterio.open(path) as src:
        arrays.append(src.read())
        profile = src.profile

    print(f"Loaded {year}")

# stack to (time, bands, height, width)
stack = np.stack(arrays)

# median composite ignoring NaN
composite = np.nanmedian(stack, axis=0)

profile.update(
    dtype=rasterio.float32,
    nodata=np.nan
)

out_path = os.path.join(out, "sentinel2_median_composite.tif")

with rasterio.open(out_path, "w", **profile) as dst:
    dst.write(composite.astype(np.float32))

print(f"\nSaved composite: {out_path}")