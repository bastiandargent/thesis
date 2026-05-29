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
predictor_path = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "stacked",
    "predictor_stacked_uncorrelated.tif",
)

exposed_mask_path = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "cov_vs_exp",
    "exposed_mask.tif",
)

covered_mask_path = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "cov_vs_exp",
    "covered_mask.tif",
)

output_terrain_mask = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "cov_vs_exp",
    "terrain_mask.tif",
)


# load input rasters
with rasterio.open(predictor_path) as src_pred:
    predictor = src_pred.read(1)  # only need one band for valid mask
    profile = src_pred.profile.copy()

with rasterio.open(exposed_mask_path) as src_mask:
    exposed_mask = src_mask.read(1)

with rasterio.open(covered_mask_path) as src_mask:
    covered_mask = src_mask.read(1)


# valid is a boolean mask where value "True" is not NaN and "False" is NaN.
valid = ~np.isnan(predictor)

# create terrain raster with NaN values.
terrain = np.full(exposed_mask.shape, np.nan, dtype="float32")


terrain[(exposed_mask == 1) & valid] = 1  # exposed
terrain[(covered_mask == 1) & valid] = 2  # covered


# check whether there is any overlap between exposed and covered masks (should not happen)
overlap = (exposed_mask == 1) & (covered_mask == 1)
if np.any(overlap):
    print("Warning: Overlap between exposed and covered masks detected!")


profile.update(dtype="float32", count=1, nodata=np.nan)

with rasterio.open(output_terrain_mask, "w", **profile) as dst:
    dst.write(terrain, 1)

print("Terrain mask created:", output_terrain_mask)
