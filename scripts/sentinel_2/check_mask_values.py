import rasterio
import numpy as np
import os

composite_folder = r"E:/Lund/sentinel_2_data/composite"

for file in os.listdir(composite_folder):
    if file.endswith(".tif") and not file.endswith("_validmask.tif"):

        path = os.path.join(composite_folder, file)

        with rasterio.open(path) as src:
            data = src.read()

        flat = data.flatten()
        flat = flat[~np.isnan(flat)]

        print(file)
        print("  Min:", np.min(flat))
        print("  Max:", np.max(flat))
        print("  99th percentile:", np.percentile(flat, 99))
        print("-" * 40)