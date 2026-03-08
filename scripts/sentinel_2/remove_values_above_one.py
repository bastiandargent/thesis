import os
import rasterio
import numpy as np

input_folder = "/home/basti/Documents/Lund/Master_Thesis/02_raw_data"
output_folder = "/home/basti/Documents/Lund/Master_Thesis/03_processed/sentinel_2/clean"

os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(input_folder):

    if not file.endswith(".tif"):
        continue

    input_path = os.path.join(input_folder, file)
    output_path = os.path.join(output_folder, file)

    with rasterio.open(input_path) as src:

        data = src.read().astype("float32")
        data[data > 1] = np.nan

        profile = src.profile

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(data)

    print("Processed:", file)

print("Done.")
