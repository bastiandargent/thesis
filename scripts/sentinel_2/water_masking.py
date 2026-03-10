import rasterio
import numpy as np

input_path = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/composite/sentinel2_median_composite.tif"
output_path = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/composite/sentinel2_nowater.tif"

with rasterio.open(input_path) as src:
    data = src.read().astype("float32")
    profile = src.profile

# Sentinel-2 bands
B02, B03, B04, B08, B11, B12 = data

# MNDWI
mndwi = (B03 - B11) / (B03 + B11)

# water mask
water_mask = mndwi > 0

# mask water in all bands
data[:, water_mask] = np.nan

profile.update(nodata=np.nan)

with rasterio.open(output_path, "w", **profile) as dst:
    dst.write(data)

print("Water masked using MNDWI")

# optional stats
water_pixels = np.sum(water_mask)
total_pixels = water_mask.size

print(f"Water pixels: {water_pixels}")
print(f"Water percentage: {water_pixels/total_pixels*100:.2f}%")