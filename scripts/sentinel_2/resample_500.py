import os
import rasterio
from rasterio.enums import Resampling

input_raster = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/composite/sentinel2_median_composite.tif"

output_raster = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/composite/sentinel2_composite_500m.tif"

scale = 50  # 10 m to 500 m


with rasterio.open(input_raster) as src:

    new_height = src.height // scale
    new_width = src.width // scale

    data = src.read(
        out_shape=(
            src.count,
            new_height,
            new_width
        ),
        resampling=Resampling.average
    )

    transform = src.transform * src.transform.scale(
        src.width / new_width,
        src.height / new_height
    )

    profile = src.profile
    profile.update(
        height=new_height,
        width=new_width,
        transform=transform,
        compress="deflate"
    )

    with rasterio.open(output_raster, "w", **profile) as dst:
        dst.write(data)

print(f"Saved 500 m raster: {output_raster}")