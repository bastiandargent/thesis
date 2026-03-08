import os
import yaml
import requests
from datetime import datetime, timezone
from get_temp_token_s2 import get_token

"""
What the script does:
- open and extract yaml parameters
- authentication to API
- mask no data, saturated, clouds, cloud shadow, cirrus
- send payload to sentinel-hub API & save response and metadata
"""


# open and extract yaml parameters

with open(r"C:\Users\Basti\Documents\uni_lund\GISM01\04_machine_learning\configs\config_s2.yaml", "r") as f:
    config = yaml.safe_load(f)

xmin = config["bbox"]["xmin"]
ymin = config["bbox"]["ymin"]
xmax = config["bbox"]["xmax"]
ymax = config["bbox"]["ymax"]
crs = config["bbox"]["crs"]

resolution = config["resolution"]
tile_size = config["tiling"]["tile_size"]

seasonal_windows = config["sentinel2"]["seasonal_windows"]
max_cloud = config["sentinel2"]["max_cloud_coverage"]

output_folder = config["output_folder"]


# authentication to API from get_temp_token_s2 script
access_token = get_token()

headers = {
    "Authorization": f"Bearer {access_token}"
}



# mask no data, saturated, clouds, cloud shadow, cirrus (keep snow/glaciers)
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B02","B03","B04","B08","B11","B12","SCL"],
    output: {
      bands: 6,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {

if (sample.SCL === 0 ||
    sample.SCL === 1 ||
    sample.SCL === 3 ||
    sample.SCL === 8 ||
    sample.SCL === 9 ||
    sample.SCL === 10) {

    return [NaN, NaN, NaN, NaN, NaN, NaN];
}

  return [
    sample.B02,
    sample.B03,
    sample.B04,
    sample.B08,
    sample.B11,
    sample.B12
  ];
}
"""


# for each specified timeframe (2022-2025, August-September), query scenes & download



for window in seasonal_windows:
    # resets counter after every year folder, so that all tiles have the same name
    tile_counter = 0

    year = window["year"]
    date_from = window["from"]
    date_to = window["to"]

    # For every year create a folder
    year_folder = os.path.join(output_folder, str(year))
    os.makedirs(year_folder, exist_ok=True)


    # send payload to sentinel-hub API & save response and metadata
    for x in range(xmin, xmax, tile_size):
        for y in range(ymin, ymax, tile_size):

            bbox = [x, y, x + tile_size, y + tile_size]

            width = int(tile_size / resolution)
            height = int(tile_size / resolution)

            payload = {
                "input": {
                    "bounds": {
                        "bbox": bbox,
                        "properties": {
                            "crs": f"http://www.opengis.net/def/crs/EPSG/0/{crs}"
                        }
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": date_from,
                                "to": date_to
                            },
                            "maxCloudCoverage": max_cloud,
                            "mosaickingOrder": "leastCC"
                        }
                    }]
                },
                "output": {
                    "width": width,
                    "height": height,
                    "responses": [{
                        "identifier": "default",
                        "format": {"type": "image/tiff"}
                    }],
                    "metadata": {
                        "bounds": True
                    }
                },
                "evalscript": evalscript
            }

            print(f"Downloading Year {year} Tile {tile_counter}")

            response = requests.post(
                "https://services.sentinel-hub.com/api/v1/process",
                headers=headers,
                json=payload,
                stream=True
            )

            if response.status_code == 200:

                filename = os.path.join(year_folder, f"tile_{tile_counter}.tif")

                with open(filename, "wb") as f:
                    f.write(response.content)

            else:
                print(f"Error {response.status_code}")
                print(response.text)

            tile_counter += 1

        
# metadata

metadata = os.path.join(output_folder, f"metadata.txt")

with open(metadata, "w") as m:
    m.write("Dataset: Sentinel-2 L2A\n")
    m.write("Source: Sentinel Hub Process API\n\n")

    m.write(f"Download Date: {datetime.now(timezone.utc)}\n")
    m.write(f"BBOX: {bbox}\n")
    m.write(f"CRS: EPSG:{crs}\n")
    m.write(f"Resolution: {resolution} m\n")
    m.write(f"Tile Size: {tile_size} m\n")
    m.write(f"Max cloud coverage: {max_cloud}%\n")
    m.write(f"Bands: B02 B03 B04 B08 B11 B12\n")
    m.write("Masked SCL classes: 0,1,3,8,9,10\n\n")
    for window in seasonal_windows:
        m.write(f"Year {window['year']}: {window['from']} to {window['to']}\n")

print("\nFinished Downloading.")