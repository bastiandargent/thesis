import rasterio
import numpy as np

path = r"E:/Lund/sentinel_2_data/2022/tile_0.tif"

with rasterio.open(path) as src:
    data = src.read()   # shape: (bands, height, width)

print("Min:", np.nanmin(data))
print("Max:", np.nanmax(data))