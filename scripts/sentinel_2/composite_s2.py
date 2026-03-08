import os
import numpy as np
import rasterio

# create folder "E:/Lund/sentinel_2_data/composite"
root_folder = r"E:/Lund/sentinel_2_data"
output_folder = os.path.join(root_folder, "composite")
os.makedirs(output_folder, exist_ok=True)

# iterate over tifs in "E:/Lund/sentinel_2_data/2022"
years = [2022, 2023, 2024, 2025]
first_year_folder = os.path.join(root_folder, str(years[0]))
tile_files = [f for f in os.listdir(first_year_folder) if f.endswith(".tif")]

print(f"Found {len(tile_files)} tiles.")

for tile_file in tile_files:

    print(f"\nProcessing {tile_file}")

    # yearly_arrays contains all raster pixel values of all tiles
    # Same tiles of different years are next to each other
    yearly_arrays = []

    # Load all years for this tile
    for year in years:
        
        # path = "E:/Lund/sentinel_2_data/{year}/{tile_file}"
        path = os.path.join(root_folder, str(year), tile_file)

        if not os.path.exists(path):
            print(f"Missing {path}")
            continue

        with rasterio.open(path) as src:
            data = src.read()  # shape: (bands, height, width)
            profile = src.profile

        yearly_arrays.append(data)

    if len(yearly_arrays) == 0:
        print("No data found. Skipping.")
        continue

    # Stack across time -> shape: (time, bands, height, width)
    stack = np.stack(yearly_arrays, axis=0)

    print(len(yearly_arrays))

    # median composite
    composite = np.nanmedian(stack, axis=0)

    # Pixel valid if at least one year had valid data
    valid_mask = ~np.all(np.isnan(stack), axis=0)

    # Convert boolean to uint8 (0/1)
    valid_mask = valid_mask.astype(np.uint8)

    # -------------------------
    # SAVE COMPOSITE
    # -------------------------

    profile.update(
        dtype=rasterio.float32,
        count=composite.shape[0],
        nodata=np.nan
    )

    composite_path = os.path.join(output_folder, tile_file)

    with rasterio.open(composite_path, "w", **profile) as dst:
        dst.write(composite.astype(np.float32))

    # -------------------------
    # SAVE VALID MASK
    # -------------------------

    mask_profile = profile.copy()
    mask_profile.update(
        dtype=rasterio.uint8,
        count=1,
        nodata=0
    )

    mask_path = os.path.join(output_folder, tile_file.replace(".tif", "_validmask.tif"))

    with rasterio.open(mask_path, "w", **mask_profile) as dst:
        dst.write(valid_mask[0], 1)

    print("Saved composite and mask.")

print("\nCompositing complete.")