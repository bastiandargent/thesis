import os
import numpy as np
import rasterio
import yaml

# load config
with open(
    r"/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml",
    "r",
) as f:
    config = yaml.safe_load(f)

# paths
input_folder = os.path.join(
    config["base_dir"], "03_processed", "sentinel_2", config["project_name"], "merge"
)

output_folder = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "composite",
)

os.makedirs(output_folder, exist_ok=True)

# find all tif files automatically
tif_files = [
    os.path.join(input_folder, f)
    for f in os.listdir(input_folder)
    if f.endswith(".tif")
]

tif_files = sorted(tif_files)  # ensure consistent order

print(f"Found {len(tif_files)} files")

arrays = []

for path in tif_files:
    with rasterio.open(path) as src:
        arrays.append(src.read())
        # stores only the last profile but they are all the same
        profile = src.profile

    print(f"Loaded {os.path.basename(path)}")

# stack: (time, bands, height, width)
stack = np.stack(arrays)

# median composite (ignore NaNs)
composite = np.nanmedian(stack, axis=0)

# update profile
profile.update(dtype=rasterio.float32, nodata=np.nan)

output_raster = os.path.join(output_folder, "sentinel2_median_composite.tif")

with rasterio.open(output_raster, "w", **profile) as dst:
    dst.write(composite.astype(np.float32))

print(f"\nSaved composite: {output_raster}")
