# Sikkim NER Landslide Susceptibility Demo — Project State & Implementation Plan

## 1. Purpose

This document is the single source of truth for the current Sikkim landslide-susceptibility demo.

The goal is to build a **working machine-learning landslide susceptibility model for an NER (North-Eastern Region) state**, using **Sikkim** as the demonstration state.

The earlier Noney/Manipur work is only the reference implementation. The final demo is **not Manipur-specific**.

The intended workflow is:

1. Prepare a DEM for the Sikkim study area.
2. Derive terrain factors.
3. Prepare a real landslide inventory.
4. Prepare lithology.
5. Skip fault distance for now.
6. Create pixel-level training samples.
7. Train an XGBoost classifier.
8. Generate a continuous susceptibility probability raster.
9. Validate and visualize the result.
10. Produce reproducible documentation.

## 2. Current model: 6 factors

The original Noney approach used seven factors:

- Elevation
- Slope
- Aspect
- Curvature
- TWI
- Fault distance
- Lithology

For this Sikkim demo, **fault distance is intentionally skipped**.

Reason: the GEM active-fault dataset contains 13,696 global features, but a spatial query against the exact Sikkim study area returned **0 intersecting faults**.

Therefore we will not invent or infer a fault-distance layer.

The current model is:

1. Elevation
2. Slope
3. Aspect
4. Curvature
5. TWI
6. Lithology

## 3. Project root

All work is under:

`/home/admin/Desktop/lhasa_porject`

Virtual environment:

`/home/admin/Desktop/lhasa_porject/.venv`

Activate it before Python project work:

```bash
cd /home/admin/Desktop/lhasa_porject
source .venv/bin/activate
```

## 4. Raw DEM data

Directory:

`data/raw/dem/`

The directory contains several HGT/ZIP files plus:

`data/raw/dem/rasters_SRTMGL1.tar.gz`

The individual N23/N24/N25 HGT tiles were discovered to be the wrong geographic region for the Sikkim demo.

The useful Sikkim DEM was found inside the TAR.GZ archive:

`output_SRTMGL1.tif`

It was checked and covers approximately:

- Longitude: 87.9998611 to 88.7998611 E
- Latitude: 27.2001389 to 27.8001389 N
- Pixel size: 0.0002777778 degrees
- NoData: -32768

## 5. Sikkim source DEM

The archive DEM was copied to:

`data/raw/dem/sikkim/study_dem.tif`

Verified:

```text
Size: 2880 × 2160
Pixel size: 0.000277777777778 × -0.000277777777778
Upper Left: 87.9998611, 27.8001389
Lower Right: 88.7998611, 27.2001389
NoData: -32768
```

The working geographic DEM was clipped to the useful common study extent:

```text
88.073595 to 88.799861 E
27.200139 to 27.544821 N
```

Output:

`data/processed/dem/sikkim_dem.tif`

Verified:

```text
Size: 2616 × 1242
Pixel size: 0.000277777777778 × -0.000277777777778
Upper Left: 88.0733333, 27.5450000
Lower Right: 88.8000000, 27.2000000
NoData: -32768
```

## 6. Master modelling grid

The DEM was reprojected to:

**EPSG:32645 — WGS 84 / UTM zone 45N**

Output:

`data/processed/dem/utm/sikkim_dem_utm.tif`

Verified:

```text
Size: 2411 × 1303
Pixel size: 30 m × 30 m
Upper Left: 605970, 3048120
Lower Right: 678300, 3009030
NoData: -32768
CRS: EPSG:32645
```

This is the master modelling grid. Every predictor raster must match this grid exactly.

## 7. Landslide inventory

Source:

`data/raw/landslides/isro/Google_Earth_landslides_polygon_21Dec2021.shp`

Original verification:

```text
Geometry: 3D Polygon
Feature Count: 255
CRS: EPSG:4326
Extent:
88.073595 to 88.894481 E
27.085676 to 27.544821 N
```

The processed inventory is:

`data/processed/landslides/sikkim_landslides.shp`

It contains:

```text
Feature Count: 172
Geometry: 3D Polygon
CRS: EPSG:4326
Extent:
88.073595 to 88.797633 E
27.200000 to 27.544821 N
```

The source inventory has fields such as Slope, Aspect, Curvature and Elevation, but the model uses factors derived from the DEM instead of relying on those attributes.

There were Shapefile field-width warnings for some Curvature attributes. Those attributes are not used as the authoritative terrain factors.

## 8. Landslide validation

Script:

`scripts/validate_landslides.py`

Command:

```bash
python scripts/validate_landslides.py
```

Result:

```text
Total landslide polygons: 172

======================================
LANDSLIDE VALIDATION
======================================
Total polygons              : 172
Intersecting DEM            : 172
With all 6 factors valid    : 167
Excluded                    : 5
======================================
```

Interpretation:

- All 172 processed polygons intersect the modelling DEM.
- 167 have usable pixels for all six predictors.
- 5 intersect locations where at least one predictor is NoData.
- We will not invent values for those locations.

## 9. Elevation

Source/final raster:

`data/processed/dem/utm/sikkim_dem_utm.tif`

This is the elevation predictor.

## 10. Slope

Final:

`data/processed/factors/slope.tif`

Generated from the UTM DEM using:

```bash
gdaldem slope   data/processed/dem/utm/sikkim_dem_utm.tif   data/processed/factors/slope.tif   -compute_edges
```

Verified:

```text
Size: 2411 × 1303
Resolution: 30 m
CRS: EPSG:32645
NoData: -9999
```

The earlier geographic-CRS slope calculation was superseded by the UTM calculation. Use the UTM-derived slope.

## 11. Aspect

Final:

`data/processed/factors/aspect.tif`

Generated using:

```bash
gdaldem aspect   data/processed/dem/utm/sikkim_dem_utm.tif   data/processed/factors/aspect.tif   -compute_edges
```

Verified:

```text
Size: 2411 × 1303
Resolution: 30 m
CRS: EPSG:32645
NoData: -9999
```

## 12. Curvature

Final:

`data/processed/factors/curvature.tif`

Verified:

```text
Size: 2411 × 1303
Resolution: 30 m
CRS: EPSG:32645
NoData: -9999
```

## 13. Hydrology and TWI

WhiteboxTools is installed in the project environment.

Python package:

`whitebox 2.3.6`

Bundled executable:

`/home/admin/Desktop/lhasa_porject/.venv/lib/python3.10/site-packages/whitebox/whitebox_tools`

Executable version:

`WhiteboxTools v2.4.0`

Filled DEM:

`data/processed/hydrology/dem_filled.tif`

Flow accumulation:

`data/processed/hydrology/flow_accumulation.tif`

The exact Whitebox tool name `FlowAccumulation` was rejected by this build during one attempted call, but a usable flow accumulation raster is present and was verified to match the modelling grid.

TWI script:

`scripts/calculate_twi.py`

TWI output:

`data/processed/hydrology/twi.tif`

Successful result:

```text
Valid pixels: 3,051,335
Minimum TWI: 5.280
Maximum TWI: 25.949
Mean TWI: 9.392
```

Verified:

```text
Size: 2411 × 1303
Resolution: 30 m
CRS: EPSG:32645
NoData: -9999
```

## 14. Lithology source data

Downloaded:

```text
data/raw/lithology/geo8alg.zip
data/raw/lithology/geo8apg.zip
```

Extracted into:

```text
data/raw/lithology/geo8alg/
data/raw/lithology/geo8apg/
```

### geo8alg

`data/raw/lithology/geo8alg/geo8alg.shp`

```text
Geometry: Line String
Feature Count: 9943
CRS: EPSG:4326
```

### geo8apg

`data/raw/lithology/geo8apg/geo8apg.shp`

```text
Geometry: Polygon
Feature Count: 3014
CRS: EPSG:4326
```

`geo8apg` was selected because we need areal geological classes for rasterization.

## 15. Sikkim lithology

A spatial query found **6 geo8apg polygons** intersecting the Sikkim study area.

Extracted layer:

`data/processed/lithology/sikkim_lithology.gpkg`

Layer:

`sikkim_lithology`

Properties:

```text
Geometry: Polygon
Feature Count: 6
CRS: EPSG:32645
```

The six polygons contain three geological codes:

```text
pC = 4 polygons
Pz = 1 polygon
Ki = 1 polygon
```

## 16. Lithology encoding

Added field:

`lith_id`

Mapping:

```text
pC = 1
Pz = 2
Ki = 3
```

These are categorical IDs, not severity rankings.

Verified:

```text
pC   1   4
Pz   2   1
Ki   3   1
```

## 17. Lithology raster

Final:

`data/processed/factors/lithology.tif`

Rasterized onto the exact 30-m modelling grid.

Initial pixel counts were:

```text
Value 0:    45,404
Value 1: 2,696,882
Value 2:   292,970
Value 3:   106,277
```

The zero values represented areas not covered by the extracted geology polygons and were changed to NoData.

Final meaning:

```text
1 = pC
2 = Pz
3 = Ki
-9999 = NoData / unmapped geology
```

Final metadata:

```text
Size: 2411 × 1303
Pixel size: 30 m × 30 m
NoData: -9999
Upper Left: 605970, 3048120
Lower Right: 678300, 3009030
CRS: EPSG:32645
```

Approximately 1.45% of the original grid was unmapped geology, so those locations will be excluded from model training/prediction where necessary.

## 18. Fault investigation

GEM source:

`data/raw/faults/gem/shapefile/gem_active_faults_harmonized.shp`

Properties:

```text
Geometry: Line String
Feature Count: 13696
CRS: EPSG:4326
Global extent
```

A direct spatial query against:

```text
88.073595 to 88.799861 E
27.200139 to 27.544821 N
```

returned:

```text
total = 0
```

Therefore:

**Fault distance is intentionally skipped.**

Do not use:

`data/processed/faults/sikkim_faults.gpkg`

as a predictor; the extracted layer is empty.

## 19. Six-factor inventory

The final predictors are:

```text
Elevation:
data/processed/dem/utm/sikkim_dem_utm.tif

Slope:
data/processed/factors/slope.tif

Aspect:
data/processed/factors/aspect.tif

Curvature:
data/processed/factors/curvature.tif

TWI:
data/processed/hydrology/twi.tif

Lithology:
data/processed/factors/lithology.tif
```

All six were checked with Rasterio and returned:

```text
shape   : (1303, 2411)
res     : (30.0, 30.0)
CRS     : EPSG:32645
aligned : True
```

This means the same row/column represents the same ground location in every predictor.

## 20. Why alignment is important

A training row can now safely combine:

```text
elevation
slope
aspect
curvature
twi
lithology
target
```

For example:

```csv
elevation,slope,aspect,curvature,twi,lithology,target
2100.1,28.5,120.3,-0.22,4.8,1,1
1750.4,19.3,45.2,0.12,5.5,2,0
```

Every predictor in a row comes from the same 30-m ground pixel.

## 21. Immediate next step: landslide label raster

The next artifact is:

`data/processed/labels/landslide_mask.tif`

Meaning:

```text
1 = landslide
0 = non-landslide
```

Create it with:

```bash
cd /home/admin/Desktop/lhasa_porject

mkdir -p data/processed/labels

gdal_rasterize   -burn 1   -init 0   -a_nodata 0   -ot Byte   -tr 30 30   -te 605970 3009030 678300 3048120   -co COMPRESS=LZW   data/processed/landslides/sikkim_landslides.shp   data/processed/labels/landslide_mask.tif
```

Important: for the label raster, zero is intentionally **non-landslide**, not missing data.

## 22. Training-data generation

After the label raster is validated, build a valid-pixel mask:

```text
elevation valid
AND slope valid
AND aspect valid
AND curvature valid
AND TWI valid
AND lithology valid
```

Positive samples:

```text
landslide_mask == 1
AND all six predictors valid
```

Negative samples:

```text
landslide_mask == 0
AND all six predictors valid
```

The initial target is:

```text
25,000 positive
25,000 negative
50,000 total
```

This broadly matches the balanced sample design used in the reference Noney workflow.

Do not simply use every pixel in every landslide polygon, because large polygons could dominate the training data.

Expected CSV:

`data/processed/training/sikkim_training.csv`

Columns:

```text
elevation
slope
aspect
curvature
twi
lithology
target
```

## 23. Model training

Reference model: XGBoost binary classifier.

Starting hyperparameters:

```text
n_estimators = 100
max_depth = 10
learning_rate = 0.1
```

Features:

```text
elevation
slope
aspect
curvature
twi
lithology
```

Target:

```text
1 = landslide
0 = non-landslide
```

Potential model output:

`models/trained_model_sikkim_6factors.pkl`

These hyperparameters are a starting point. The final model should be evaluated rather than assuming the Noney score transfers to Sikkim.

## 24. Validation strategy

A naive random pixel split can produce overly optimistic results because neighboring pixels are spatially correlated.

Preferred validation:

**spatially aware train/test validation**

For example:

- divide the study area into spatial blocks
- keep held-out blocks separate from training
- evaluate on spatially unseen areas

Report:

- Precision
- Recall
- F1
- ROC-AUC
- Confusion matrix

Do not claim a specific Sikkim F1 score before the model has actually been trained and evaluated.

## 25. Susceptibility prediction

After training, predict the positive-class probability for every valid modelling pixel.

Conceptually:

```text
0.0 = lower predicted susceptibility
1.0 = higher predicted susceptibility
```

Expected output:

`data/processed/results/sikkim_susceptibility_6factor.tif`

This should remain a continuous probability raster.

## 26. Expected final outputs

```text
data/processed/results/sikkim_susceptibility_6factor.tif
data/processed/results/sikkim_susceptibility_6factor.png
data/processed/results/model_metrics_sikkim.json
models/trained_model_sikkim_6factors.pkl
```

## 27. Recommended project structure

```text
/home/admin/Desktop/lhasa_porject/

├── .venv/
├── data/
│   ├── raw/
│   │   ├── dem/
│   │   ├── landslides/isro/
│   │   ├── lithology/
│   │   └── faults/gem/
│   │
│   └── processed/
│       ├── dem/
│       │   ├── sikkim_dem.tif
│       │   └── utm/sikkim_dem_utm.tif
│       ├── factors/
│       │   ├── slope.tif
│       │   ├── aspect.tif
│       │   ├── curvature.tif
│       │   └── lithology.tif
│       ├── hydrology/
│       │   ├── dem_filled.tif
│       │   ├── flow_accumulation.tif
│       │   └── twi.tif
│       ├── landslides/
│       │   └── sikkim_landslides.shp
│       ├── lithology/
│       │   └── sikkim_lithology.gpkg
│       ├── faults/
│       │   └── sikkim_faults.gpkg  # empty/not used
│       ├── labels/
│       │   └── landslide_mask.tif
│       ├── training/
│       │   └── sikkim_training.csv
│       └── results/
│           ├── sikkim_susceptibility_6factor.tif
│           ├── sikkim_susceptibility_6factor.png
│           └── model_metrics_sikkim.json
│
├── scripts/
│   ├── calculate_twi.py
│   ├── validate_landslides.py
│   ├── build_training_dataset.py
│   ├── train_model.py
│   └── predict_susceptibility.py
│
└── models/
    └── trained_model_sikkim_6factors.pkl
```

## 28. Current checklist

### Data acquisition

- [x] Sikkim DEM found
- [x] Real ISRO/Google Earth landslide inventory obtained
- [x] USGS geology obtained
- [x] GEM faults obtained
- [x] GEM checked; zero faults in exact study area

### Spatial preprocessing

- [x] DEM clipped
- [x] DEM reprojected to EPSG:32645
- [x] DEM standardized to 30 m
- [x] Slope generated
- [x] Aspect generated
- [x] Curvature generated
- [x] Hydrology DEM filled
- [x] Flow accumulation available
- [x] TWI generated
- [x] Lithology extracted
- [x] Lithology encoded
- [x] Lithology rasterized
- [x] Lithology NoData corrected
- [x] Six-factor grid alignment validated

### Landslide validation

- [x] 172 processed landslide polygons
- [x] 172 intersect DEM
- [x] 167 have all six factors valid
- [x] 5 excluded from all-factor-valid locations

### Machine learning

- [x] Landslide mask (`data/processed/labels/landslide_mask.tif`)
- [x] Valid training mask (3,000,725 valid 6-factor pixels)
- [x] Positive sampling (3,106 valid landslide pixels)
- [x] Negative sampling (3,106 balanced non-landslide pixels)
- [x] Training CSV (`data/processed/training/sikkim_training.csv`)
- [x] Spatial train/test split & 5-fold cross-validation
- [x] XGBoost training (`models/trained_model_sikkim_6factors.pkl`)
- [x] Model evaluation (86.16% Acc, 86.48% F1, 93.80% ROC-AUC)
- [x] Full-area prediction (3,000,725 pixels inferred)
- [x] Susceptibility map (`data/processed/results/sikkim_susceptibility_6factor.tif` & `.png`)
- [x] Independent validation on Pan-NER historical event catalog
- [x] Final documentation

## 29. Exact next action

The next action is to create and validate:

`data/processed/labels/landslide_mask.tif`

Then the workflow is:

```text
LANDSLIDE MASK
      ↓
VALID 6-FACTOR PIXELS
      ↓
BALANCED TRAINING SAMPLES
      ↓
TRAINING CSV
      ↓
SPATIAL TRAIN/TEST SPLIT
      ↓
XGBOOST
      ↓
MODEL METRICS
      ↓
FULL-AREA PREDICTION
      ↓
SUSCEPTIBILITY MAP
```

## 30. Key decisions

1. Sikkim is the actual NER demo state.
2. Noney/Manipur is only the reference implementation.
3. The current model has six factors.
4. Fault distance is skipped because GEM has zero mapped fault features in the exact study area.
5. Do not invent fault values.
6. Use EPSG:32645 and the 30-m modelling grid.
7. Use DEM-derived terrain factors.
8. Use the real 172-polygon landslide inventory for labels.
9. Exclude locations where any predictor is NoData.
10. Do not assume the Noney model's performance transfers to Sikkim.
11. Prefer spatially aware validation.
12. Keep all generated data and scripts under the project structure for reproducibility.

## 31. One-sentence summary

**We are building a reproducible six-factor XGBoost landslide-susceptibility demo for Sikkim using a real ISRO landslide inventory, a 30-m SRTM DEM, derived terrain/hydrology factors, and regional USGS lithology, with fault distance intentionally omitted because GEM has no mapped faults in the selected study area.**
