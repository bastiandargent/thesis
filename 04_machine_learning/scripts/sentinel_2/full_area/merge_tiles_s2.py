import os
import rasterio
from rasterio.merge import merge
import yaml


with open(
    r"/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml",
    "r",
) as f:
    config = yaml.safe_load(f)

input_folder = os.path.join(
    config["base_dir"], "03_processed", "sentinel_2", config["project_name"], "clean"
)
output_folder = os.path.join(
    config["base_dir"], "03_processed", "sentinel_2", config["project_name"], "merge"
)

os.makedirs(output_folder, exist_ok=True)


# merge tiles for each year separately and save as geotiffs.

years = [2022, 2023, 2024, 2025]

for year in years:
    tiles = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.startswith(str(year)) and f.endswith(".tif")
    ]

    print(f"{year}: {len(tiles)} tiles")

    srcs = [rasterio.open(t) for t in tiles]

    # merge tiles for the year
    mosaic, transform = merge(srcs)

    out_path = os.path.join(output_folder, f"{year}_mosaic.tif")

    # manually define metadata for new merged output files
    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=mosaic.shape[1],
        width=mosaic.shape[2],
        count=mosaic.shape[0],
        dtype=mosaic.dtype,
        crs=srcs[0].crs,
        transform=transform,
        compress="deflate",
    ) as dst:
        dst.write(mosaic)

    for s in srcs:
        s.close()

    print(f"Saved {out_path}")
