import numpy as np
import rasterio
import yaml
import os


with open(
    r"/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml",
    "r",
) as f:
    config = yaml.safe_load(f)


s2 = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "composite",
    "sentinel2_resampled.tif",
)
# if you didn't resample, you can use this instead:
# s2 = os.path.join(config["base_dir"], "03_processed", "sentinel_2", config["project_name"], "indices", "s2_band_ratios.tif")


dem = os.path.join(
    config["base_dir"], "03_processed", "dem", config["project_name"], "dem_clipped.tif"
)
gravity = os.path.join(
    config["base_dir"],
    "03_processed",
    "gravity",
    config["project_name"],
    "gravity_resampled.tif",
)

output_raster = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "stacked",
    "predictor_stacked.tif",
)

os.makedirs(os.path.dirname(output_raster), exist_ok=True)


with rasterio.open(s2) as src_s2:
    s2_data = src_s2.read().astype("float32")
    profile = src_s2.profile

with rasterio.open(dem) as src_dem:
    dem_data = src_dem.read().astype("float32")

with rasterio.open(gravity) as src_grav:
    grav_data = src_grav.read(1).astype("float32")

print("S2 shape:", s2_data.shape)
print("DEM shape:", dem_data.shape)
print("GRAV shape:", grav_data.shape)

# stack in the order of S2 bands, then DEM, then gravity
# grav_data[np.newaxis, :, :] adds a new axis to make it compatible for stacking (e.g. (2500, 2500) -> (1, 2500, 2500))
stack = np.vstack([s2_data, dem_data, grav_data[np.newaxis, :, :]])

profile.update(count=stack.shape[0], dtype="float32", compress="deflate")


with rasterio.open(output_raster, "w", **profile) as dst:
    dst.write(stack)


print("Predictor stack saved:", output_raster)