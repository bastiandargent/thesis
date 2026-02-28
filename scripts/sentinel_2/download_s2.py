import os
import requests
from get_temp_token_s2 import get_token

access_token = get_token()

headers = {
    "Authorization": f"Bearer {access_token}"
}

evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B02","B03","B04","B08","B11","B12"],
    output: {
      bands: 6,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  return [sample.B02, sample.B03, sample.B04,
          sample.B08, sample.B11, sample.B12];
}
"""

output_folder = r"E:\Lund\sentinel_2_data"

tile_size = 10000
resolution = 10

xmin = 649797
ymin = 7526750
xmax = 699797
ymax = 7576750

tile_id = 0

for x in range(xmin, xmax, tile_size):
    for y in range(ymin, ymax, tile_size):

        bbox = [
            x,
            y,
            (x + tile_size),
            (y + tile_size)
        ]

        payload = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {
                        "crs": "http://www.opengis.net/def/crs/EPSG/0/3006"
                    }
                },
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": "2024-09-15T00:00:00Z",
                            "to": "2024-09-15T23:59:59Z"
                        },
                        "mosaickingOrder": "leastCC"
                    }
                }]
            },
            "output": {
                "width": 1000,
                "height": 1000,
                "responses": [{
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }]
            },
            "evalscript": evalscript
        }

        print(f"Downloading tile {tile_id} | BBOX: {bbox}")

        response = requests.post(
            "https://services.sentinel-hub.com/api/v1/process",
            headers=headers,
            json=payload,
            stream=True
        )
        
        print(response.status_code)
        print(response.headers.get("Content-Type"))

        if response.status_code == 200:
            filename = os.path.join(output_folder, f"tile_{tile_id}.tif")
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Saved: {filename}")
        else:
            print(f"Error {response.status_code}")
            print(response.text)

        tile_id += 1

print("Download complete.")
