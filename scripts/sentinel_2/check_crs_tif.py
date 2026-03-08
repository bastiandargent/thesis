import rasterio

with rasterio.open(r'E:\Lund\sentinel_2_data\tile_0.tif') as src:
    crs = src.crs
    print(crs)
