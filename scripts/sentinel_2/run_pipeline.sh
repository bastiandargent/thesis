#!/bin/bash

#python download_sentinel.py
python remove_values_above_one.py
python merge_tiles_s2.py
python composite_s2.py
python resample_500.py
# python derive_indices.py
python water_masking.py # rewrite correct folder after finishing those scripts