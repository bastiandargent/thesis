import rasterio
import numpy as np

path = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/composite/sentinel2_median_composite.tif"

with rasterio.open(path) as src:
    data = src.read()

total_pixels = data.size
nan_pixels = np.isnan(data).sum()

print(f"Total pixels: {total_pixels}")
print(f"NaN pixels: {nan_pixels}")
print(f"NaN percentage: {nan_pixels/total_pixels*100:.2f}%")

# per-band stats
for b in range(data.shape[0]):
    band = data[b]
    nan_count = np.isnan(band).sum()
    print(f"Band {b+1}: {nan_count} NaNs ({nan_count/band.size*100:.2f}%)")