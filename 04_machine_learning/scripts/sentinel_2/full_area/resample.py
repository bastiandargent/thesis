import os
import rasterio
from rasterio.enums import Resampling
import yaml

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
    "indices",
    "s2_band_ratios.tif",
)

output_raster = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "composite",
    "sentinel2_resampled.tif",
)

scale = 5  # 20 m to 100 m

# Resample the raster using average resampling
with rasterio.open(input_raster) as src:
    new_height = src.height // scale
    new_width = src.width // scale

    data = src.read(
        out_shape=(src.count, new_height, new_width), resampling=Resampling.average
    )

    transform = src.transform * src.transform.scale(
        src.width / new_width, src.height / new_height
    )

    profile = src.profile
    profile.update(
        height=new_height, width=new_width, transform=transform, compress="deflate"
    )

    with rasterio.open(output_raster, "w", **profile) as dst:
        dst.write(data)

print(f"Saved resampled raster: {output_raster}")
