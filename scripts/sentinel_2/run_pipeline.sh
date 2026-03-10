#!/bin/bash

python download_sentinel.py
python clean_reflectance.py
python mosaic_years.py
python temporal_composite.py
python mask_water.py