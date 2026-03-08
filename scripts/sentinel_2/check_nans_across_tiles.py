import os
import rasterio
import numpy as np

composite_folder = r"E:/Lund/sentinel_2_data/composite"

for file in os.listdir(composite_folder):
    if file.endswith("_validmask.tif"):

        path = os.path.join(composite_folder, file)

        with rasterio.open(path) as src:
            mask = src.read(1)   # single band

        total_pixels = mask.size
        valid_pixels = np.sum(mask == 1)
        nan_pixels = np.sum(mask == 0)

        nan_percent = (nan_pixels / total_pixels) * 100

        print(file)
        print(f"  Total pixels: {total_pixels}")
        print(f"  Valid pixels: {valid_pixels}")
        print(f"  NaN pixels: {nan_pixels}")
        print(f"  NaN percentage: {nan_percent:.2f}%")
        print("-" * 40)