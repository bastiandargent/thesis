import os
import rasterio
import numpy as np
import yaml


# open and extract yaml parameters
with open(
    r"/home/basti/Documents/Lund/Master_Thesis/04_machine_learning/configs/config_s2.yaml",
    "r",
) as f:
    config = yaml.safe_load(f)

input_folder = os.path.join(
    config["base_dir"], "02_raw_data", "sentinel_2", config["project_name"]
)
output_folder = os.path.join(
    config["base_dir"], "03_processed", "sentinel_2", config["project_name"], "clean"
)

os.makedirs(output_folder, exist_ok=True)

# loop through all files in input folder, read, set values > 1 to NaNs and save in output folder

for file in os.listdir(input_folder):
    if not file.endswith(".tif"):
        continue

    input_path = os.path.join(input_folder, file)
    output_path = os.path.join(output_folder, file)

    with rasterio.open(input_path) as src:
        data = src.read().astype("float32")

        data[data > 1] = np.nan

        # profile is used to keep the same metadata as the original file (e.g. resolution, bands, etc.)
        profile = src.profile

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(data)

    print("Processed:", file)

print("Done.")
