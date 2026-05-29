import os
import numpy as np
import rasterio
import yaml

"""
Script to compute spectral band ratios from Sentinel-2 composite.
"""


# Input and output files

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
    "composite",
    "sentinel2_median_composite.tif",
)

output_raster = os.path.join(
    config["base_dir"],
    "03_processed",
    "sentinel_2",
    config["project_name"],
    "indices",
    "s2_band_ratios.tif",
)


# Create output folder if it does not exist
os.makedirs(os.path.dirname(output_raster), exist_ok=True)


def compute_ratio(numerator, denominator):
    """
    Compute band ratio.

    If the denominator is 0 or NaN,
    the result will be NaN.
    """

    ratio = np.divide(
        numerator,
        denominator,
        out=np.full_like(numerator, np.nan),  # fill invalid results with NaN
        where=denominator != 0,  # only divide where denominator ≠ 0
    )

    return ratio


with rasterio.open(input_raster) as src:
    # Read raster into numpy array
    data = src.read().astype("float32")

    profile = src.profile

    print("Raster shape:", data.shape)

    # extract S2 bands
    B2 = data[0]  # Blue
    B3 = data[1]  # Green
    B4 = data[2]  # Red
    B5 = data[3]  # Red edge
    B6 = data[4]  # Red edge
    B7 = data[5]  # Red edge
    B8 = data[6]  # NIR
    B11 = data[7]  # SWIR1
    B12 = data[8]  # SWIR2

    # Compute spectral band ratios

    # Vegetation / NIR ratio
    r_veg = compute_ratio(B8, B4)

    # Ferric iron indicator
    r_ferric = compute_ratio(B4, B2)

    # Ferrous iron indicator
    r_ferrous = compute_ratio(B11, B8)

    # Clay minerals
    r_clay = compute_ratio(B11, B12)

    # Carbonate indicator
    r_carb = compute_ratio(B12, B11)

    # Stack all ratios together
    ratios = np.stack([r_veg, r_ferric, r_ferrous, r_clay, r_carb])

    # Combine original bands + ratios to 15 bands
    output_raster = np.vstack((data, ratios))

    print("Output raster shape:", output_raster.shape)

    profile.update(
        count=output_raster.shape[0], dtype="float32", nodata=np.nan, compress="deflate"
    )

    with rasterio.open(output_raster, "w", **profile) as dst:
        dst.write(output_raster)

print("Saved raster:", output_raster)
