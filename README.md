## Sentinel-2 Processing Pipeline

This pipeline processes Sentinel-2 data and integrates it with preprocessed additional datasets (DEM, gravity) for lithology classification using Random Forests.

Two pipeline variants are available:
- `full_area`: evaluation across the entire study area
- `cov_vs_exp`: terrain-dependent evaluation (covered vs exposed)

## Scope and Limitations

This pipeline:
- Handles preprocessing of Sentinel-2 data only

This pipeline does NOT:
- Preprocess DEM or gravity data (done externally in QGIS)
- Create training samples (`training_samples.csv`)
    - Example instructions: `03_processed/sampling/sampling_log.txt`
- Generate terrain masks (`exposed_mask.tif`, `terrain_mask.tif`)
    - Example instructions: `03_processed/nmd_landcover/landcover_log.txt`

## Project Structure

- 02_raw_data
    - sentinel_2
- 03_processed
    - dem
    - gravity
    - sampling
    - sentinel_2
- 04_machine_learning
    - configs
    - results
    - scripts
        - sentinel_2
            - full_area
            - cov_vs_exp
    - .env
    - .gitignore

Some folders may be automatically created while running pipeline.

## Setup

### First-time setup
- sign up to sentinel-hub (free API access expires after 1 month)
    - Instructions for API Authentication: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html
- Create `.env`
    - Add CLIENT_ID & CLIENT_SECRET
- Configure `config.yaml`

### Subsequent runs
- Update `config.yaml` if needed
  - Change `project_name` to avoid overwriting previous results


## Pipeline Execution (Full Area)

1. download_s2.py  
2. remove_values_above_one.py  
3. merge_tiles_s2.py
4. composite_s2.py
   - Warning may appear but can be ignored  
5. band_ratios_s2.py  
   - Small NaN variance (~0.01%) is expected after compositing
6. resample.py  
   - Only resample S2 data if needed
   - Change variable scale depending
7. stack_predictors.py  
   - Ensure DEM and gravity inputs exist  
   - Check spatial alignment  
8. remove_correlated_predictors.py  
   - Requires `training_samples.csv`  
9. rf_spatial_cv.py
10. rf_random_cv.py  
11. predict_lithology_map.py


## Pipeline Execution (Terrain-Dependent)

Same as full pipeline with additional steps:

- snow_ice_mask.py (after merge_tiles_s2.py)
- create_terrain_mask.py (after remove_correlated_predictors.py)

Additional requirements:
- `exposed_mask.tif`
- `terrain_mask.tif`


## Notes

- Ensure all raster layers are spatially aligned before stacking in `stack_predictors.py`