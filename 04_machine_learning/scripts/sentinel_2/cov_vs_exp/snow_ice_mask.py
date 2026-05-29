import rasterio
import numpy as np
import os
import yaml

# load config
with open(
    r"/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml",
    "r",
) as f:
    config = yaml.safe_load(f)

# paths
input_folder = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "composite",
    "sentinel2_median_composite.tif",
)

output_mask = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "cov_vs_exp",
    "snow_ice_mask_ndsi.tif",
)

os.makedirs(os.path.dirname(output_mask), exist_ok=True)



# read raster bands for NDSI calculation
with rasterio.open(input_folder) as src:
    green = src.read(2).astype("float32")  # B03
    swir = src.read(8).astype("float32")  # B11
    profile = src.profile

# NDSI
ndsi = (green - swir) / (green + swir)

# avoid division by zero
ndsi = np.where((green + swir) == 0, np.nan, ndsi)

# snow + glacier detection (Hall et al.)
snow_mask = (ndsi > 0.3) & (green > 0.1)

snow_mask = snow_mask.astype("uint8")

print("Mask values:", np.unique(snow_mask))

# all values are valid, no NaNs, so we can set nodata to None
profile.update(count=1, dtype=rasterio.uint8, nodata=None, compress="lzw")

with rasterio.open(output_mask, "w", **profile) as dst:
    dst.write(snow_mask, 1)

print("Snow + ice mask (NDSI) created:", output_mask)
