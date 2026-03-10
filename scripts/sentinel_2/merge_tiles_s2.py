import os
import rasterio
from rasterio.merge import merge

folder = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/clean"
out = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/merge"

os.makedirs(out, exist_ok=True)

years = [2022, 2023, 2024, 2025]

for year in years:

    tiles = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.startswith(str(year)) and f.endswith(".tif")
    ]

    print(f"{year}: {len(tiles)} tiles")

    srcs = [rasterio.open(t) for t in tiles]
    mosaic, transform = merge(srcs)

    meta = srcs[0].meta.copy()
    meta.update(
        height=mosaic.shape[1],
        width=mosaic.shape[2],
        transform=transform,
        compress="deflate"
    )

    out_path = os.path.join(out, f"{year}_mosaic.tif")

    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(mosaic)

    for s in srcs:
        s.close()

    print(f"Saved {out_path}")