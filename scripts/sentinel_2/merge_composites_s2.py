import os
import rasterio
from rasterio.merge import merge

# -------------------------
# CONFIG
# -------------------------

input_folder = r"E:/Lund/sentinel_2_data/composite"
output_path = r"/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/"

# -------------------------
# COLLECT TILES
# -------------------------

tile_files = [
    os.path.join(input_folder, f)
    for f in os.listdir(input_folder)
    if f.endswith(".tif") and not f.endswith("_validmask.tif")
]

print(f"Found {len(tile_files)} composite tiles.")

# -------------------------
# OPEN DATASETS
# -------------------------

datasets = [rasterio.open(fp) for fp in tile_files]

# -------------------------
# MOSAIC
# -------------------------

mosaic, transform = merge(datasets)

# Use metadata from first tile
out_meta = datasets[0].meta.copy()

out_meta.update({
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": transform
})

# -------------------------
# SAVE MOSAIC
# -------------------------

with rasterio.open(output_path, "w", **out_meta) as dest:
    dest.write(mosaic)

print(f"\nMosaic saved to:\n{output_path}")

# Close datasets
for ds in datasets:
    ds.close()
