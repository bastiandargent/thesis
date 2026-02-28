import rasterio
import glob

files = glob.glob("E:/Lund/tiles/*.tif")

crs_set = set()

for f in files:
    with rasterio.open(f) as src:
        crs_set.add(str(src.crs))

print(crs_set)
