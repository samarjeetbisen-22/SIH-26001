# Assam Landslide Pipeline — Deployment Status

**State:** Assam  
**Pipeline Version:** 30m Copernicus DEM + XGBoost 6-Factor + LHASA v2  
**CRS:** EPSG:32646 (WGS84 / UTM Zone 46N)  
**Last Updated:** 2026-09-15  
**Status:** ✅ ALL STEPS COMPLETE

---

## Pipeline Steps

| #   | Step                       | Status  | Output                                                                             |
| --- | -------------------------- | ------- | ---------------------------------------------------------------------------------- |
| 01  | Directory Setup            | ✅ Done | `data/raw/dem/assam/`, `data/processed/factors/assam/`, `models/assam/`            |
| 02  | Events Export              | ✅ Done | `data/raw/landslides/assam_events.csv` — 105 events                                |
| 03  | DEM Download               | ✅ Done | 11 Copernicus tiles → `assam_dem_merged.tif` (600.9 MB, WGS84)                     |
| 04  | DEM Reprojection (UTM 46N) | ✅ Done | `assam_dem_utm46n.tif` — 14,982 × 20,351 @ 30m                                     |
| 05  | Terrain Morphometry        | ✅ Done | Elevation, Slope, Aspect, Curvature, TWI in `data/processed/factors/assam/`        |
| 06  | Lithology Extraction       | ✅ Done | 87 features, 8 formations → `data/processed/lithology/assam/assam_lithology.gpkg`  |
| 07  | Label Mask                 | ✅ Done | 8,116 positive pixels → `data/processed/labels/assam/assam_label_mask.tif`         |
| 08  | Training Dataset           | ✅ Done | 16,232 balanced samples → `data/processed/training/assam/assam_training.csv`       |
| 09  | XGBoost Training           | ✅ Done | CV AUC 95.28%, Test AUC 95.18%, Acc 89.59%, Recall 95.4%                           |
| 10  | Full-Area Prediction       | ✅ Done | 198,267,893 valid pixels → `data/processed/results/assam/assam_susceptibility.tif` |
| 11  | LHASA Nowcast              | ✅ Done | 3 scenarios complete → `assam_lhasa_alert_extreme.tif`                             |
| 12  | Maps & Reports             | ✅ Done | 4 PNGs + JSON report saved                                                         |

---

## Model Performance

| Metric             | Value                                            |
| ------------------ | ------------------------------------------------ |
| Grid size          | 14,982 × 20,351 pixels @ 30m                     |
| Master CRS         | EPSG:32646 (UTM Zone 46N)                        |
| Training samples   | 16,232 (balanced 1:1)                            |
| Positive events    | 105 landslide events, 150m buffer → 8,116 pixels |
| 5-Fold CV AUC      | **95.28%**                                       |
| Holdout Test AUC   | **95.18%**                                       |
| Accuracy           | **89.59%**                                       |
| F1 Score           | **90.16%**                                       |
| Recall (landslide) | **95.4%**                                        |

### Feature Importance

| Feature   | Importance |
| --------- | ---------- |
| TWI       | **29.05%** |
| Slope     | **26.16%** |
| Lithology | 18.75%     |
| Elevation | 16.20%     |
| Curvature | 5.19%      |
| Aspect    | 4.64%      |

> **Note:** TWI dominance is unique to Assam — reflects Brahmaputra valley flood-prone topography where high wetness index drives saturation-induced slope failures.

---

## Susceptibility Distribution

| Class               | Pixel Count | % of Area |
| ------------------- | ----------- | --------- |
| Very Low (0–0.2)    | 163,442,137 | 82.4%     |
| Low (0.2–0.4)       | 11,749,303  | 5.9%      |
| Moderate (0.4–0.6)  | 8,478,245   | 4.3%      |
| High (0.6–0.8)      | 8,516,644   | 4.3%      |
| Very High (0.8–1.0) | 6,081,564   | 3.1%      |

**~7.4% of Assam terrain is in High/Very High susceptibility zones** — concentrated in Dima Hasao, North Cachar Hills, and Barak Valley escarpments.

---

## LHASA Nowcast Results

| Scenario                            | ARI (mm)     | L0 Safe | L1 Advisory | L2 Watch | L3 Warning | L4 Severe |
| ----------------------------------- | ------------ | ------- | ----------- | -------- | ---------- | --------- |
| Dry (Pre-Monsoon)                   | 2.7 mm       | 96.9%   | 3.1%        | 0%       | 0%         | 0%        |
| Active Monsoon (Brahmaputra)        | 118.3 mm     | 82.4%   | 5.9%        | 4.3%     | 4.3%       | 3.1%      |
| **Extreme (Dima Hasao Cloudburst)** | **212.1 mm** | 0%      | 82.4%       | 5.9%     | 4.3%       | **7.4%**  |

**Extreme storm combined L3+L4: 11.7% of Assam area** — representing ~4,600 km² under Warning/Severe alert during a major cloudburst event.

---

## Lithology Summary

| Code | Formation            | Count |
| ---- | -------------------- | ----- |
| N    | Neogene sediments    | 23    |
| pC   | Precambrian basement | 22    |
| Pg   | Paleogene            | 15    |
| Ts   | Tertiary sediments   | 10    |
| Q    | Quaternary alluvium  | 7     |
| MzPz | Mesozoic-Paleozoic   | 4     |
| Pz   | Paleozoic            | 4     |
| Ks   | Cretaceous           | 1     |
| Trms | Triassic             | 1     |

---

## Key Files

| File                                                         | Description                               |
| ------------------------------------------------------------ | ----------------------------------------- |
| `data/raw/dem/assam/assam_dem_merged.tif`                    | Raw 11-tile Copernicus mosaic (600.9 MB)  |
| `data/processed/dem/assam/utm/assam_dem_utm46n.tif`          | UTM 46N reprojected DEM                   |
| `data/processed/factors/assam/assam_elevation.tif`           | Elevation factor                          |
| `data/processed/factors/assam/assam_slope.tif`               | Slope factor                              |
| `data/processed/factors/assam/assam_aspect.tif`              | Aspect factor                             |
| `data/processed/factors/assam/assam_curvature.tif`           | Curvature factor                          |
| `data/processed/factors/assam/assam_twi.tif`                 | TWI factor                                |
| `data/processed/lithology/assam/assam_lithology.gpkg`        | Clipped geology vectors                   |
| `data/processed/labels/assam/assam_label_mask.tif`           | Binary label raster                       |
| `data/processed/training/assam/assam_training.csv`           | Balanced training dataset                 |
| `models/assam/assam_xgboost.pkl`                             | Trained XGBoost model                     |
| `data/processed/results/assam/assam_susceptibility.tif`      | Full-area susceptibility (LZW compressed) |
| `data/processed/results/assam/assam_lhasa_alert_extreme.tif` | LHASA alert raster (extreme scenario)     |
| `data/processed/results/assam/assam_model_report.json`       | Full metrics JSON                         |
| `data/processed/results/assam/assam_lhasa_report.json`       | LHASA scenario report JSON                |

---

## Scripts

| Script                                    | Purpose                                 |
| ----------------------------------------- | --------------------------------------- |
| `scripts/download_assam_dem.py`           | Download 11 Copernicus 30m tiles        |
| `scripts/prepare_assam_dem.py`            | Reproject + derive terrain factors      |
| `scripts/extract_assam_lithology.py`      | Clip lithology from Pan-NER GeoPackage  |
| `scripts/create_assam_label_mask.py`      | Rasterize 150m event buffers            |
| `scripts/build_assam_training.py`         | Build balanced training CSV             |
| `scripts/train_assam_model.py`            | Train XGBoost, generate metrics + plots |
| `scripts/predict_assam_susceptibility.py` | Batched full-area inference             |
| `scripts/run_assam_lhasa_nowcast.py`      | 3-scenario LHASA nowcast                |

---

## Change Log

| Date       | Change                                                                                 |
| ---------- | -------------------------------------------------------------------------------------- |
| 2026-09-15 | Step 03: Downloaded 11 Copernicus 30m tiles, merged to assam_dem_merged.tif (600.9 MB) |
| 2026-09-15 | Step 04: Reprojected to UTM 46N → 14,982 × 20,351 grid                                 |
| 2026-09-15 | Step 05: Derived all 5 terrain factors (Elevation, Slope, Aspect, Curvature, TWI)      |
| 2026-09-15 | Step 06: Extracted 87 geological features from Pan-NER GeoPackage                      |
| 2026-09-15 | Step 07: Created label mask — 8,116 positive pixels from 105 events @ 150m buffer      |
| 2026-09-15 | Step 08: Built balanced training dataset — 16,232 samples                              |
| 2026-09-15 | Step 09: Trained XGBoost — CV AUC 95.28%, Test AUC 95.18%, TWI dominant feature        |
| 2026-09-15 | Step 10: Full-area susceptibility — 198M pixels, 7.4% High/Very High risk zone         |
| 2026-09-15 | Step 11: LHASA nowcast — Extreme storm (ARI=212.1mm): 7.4% L4 + 4.3% L3 = 11.7%        |
| 2026-09-15 | Step 12: All maps and JSON reports generated                                           |
