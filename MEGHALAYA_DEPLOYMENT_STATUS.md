# Meghalaya Landslide Susceptibility & NASA LHASA Deployment Status

## 1. Overview & Context

- **Region**: Meghalaya (Shillong Plateau, Garo Hills, Khasi Hills, Jaintia Hills)
- **High-Risk Lifelines**: NH-40 (Guwahati–Shillong Expressway), NH-44 / NH-6 (Shillong–Jowai–Silchar corridor), Cherrapunji / Mawsynram southern escarpments (world-record rainfall zone)
- **Geographical Bounds**:
  - Latitude: $25.0^\circ\text{N}$ to $26.2^\circ\text{N}$
  - Longitude: $89.9^\circ\text{E}$ to $92.6^\circ\text{E}$
- **Target Projection**: **EPSG:32646 (WGS 84 / UTM Zone 46N)**
- **Target Grid Resolution**: **30 m** ($4,552 \times 9,099$ pixels = **41.4M pixels total / 39.5M valid terrain pixels**)
- **Historical Inventory**: 39 recorded landslide events from pan-NER catalog (continuous monsoon, downpours, mining destabilization)

---

## 2. Pipeline Execution Checklist & Current Status

| Step   | Component                           |   Status    | Output / Details                                                                                                                                                                                              |
| ------ | ----------------------------------- | :---------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **01** | Directory Setup & Structure         | 🟢 Complete | Created subdirectories in `data/` and `models/`                                                                                                                                                               |
| **02** | Event Filtering & Export            | 🟢 Complete | [`data/raw/landslides/meghalaya_events.csv`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/raw/landslides/meghalaya_events.csv) (39 events)                                              |
| **03** | DEM Acquisition (SRTM GL1 30 m)     | 🟢 Complete | [`data/raw/dem/meghalaya/meghalaya_dem_merged.tif`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/raw/dem/meghalaya/meghalaya_dem_merged.tif) (42.13 MB)                                 |
| **04** | Master Grid Reprojection (UTM 46N)  | 🟢 Complete | [`data/processed/dem/meghalaya/utm/meghalaya_dem_utm46n.tif`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/dem/meghalaya/utm/meghalaya_dem_utm46n.tif) ($4,552 \times 9,099$) |
| **05** | Terrain Morphometry Derivation      | 🟢 Complete | Elevation, Slope, Aspect, Curvature, TWI derived @ 30 m                                                                                                                                                       |
| **06** | Regional Lithology Extraction       | 🟢 Complete | [`data/processed/lithology/meghalaya/meghalaya_lithology.gpkg`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/lithology/meghalaya/meghalaya_lithology.gpkg) (31 units)         |
| **07** | Label Mask Generation               | 🟢 Complete | $150\text{ m}$ circular buffers $\to$ **2,979 positive pixels**                                                                                                                                               |
| **08** | Balanced Dataset Construction       | 🟢 Complete | [`data/processed/training/meghalaya/meghalaya_training.csv`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/training/meghalaya/meghalaya_training.csv) (5,958 samples)          |
| **09** | XGBoost Model Training & CV         | 🟢 Complete | **CV AUC: 94.61%**, **Test AUC: 95.07%**, **Accuracy: 89.09%**                                                                                                                                                |
| **10** | Full-Area Susceptibility Prediction | 🟢 Complete | [`data/processed/results/meghalaya/meghalaya_susceptibility.tif`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_susceptibility.tif) (39.5M px)     |
| **11** | Dynamic NASA LHASA Nowcast          | 🟢 Complete | Evaluated across Dry, Monsoon, and Extreme Storm                                                                                                                                                              |
| **12** | Map & Report Generation             | 🟢 Complete | 5 high-res PNG maps, 2 JSON reports, 1 GeoTIFF alert raster                                                                                                                                                   |

---

## 3. Key Model & Nowcast Metrics

### Model Performance (XGBoost 6-Factor)

- **5-Fold Cross Validation**:
  - Accuracy: **88.88%**
  - F1-Score: **89.43%**
  - ROC-AUC: **94.61%**
- **Holdout Test Set (20% split, 1,192 samples)**:
  - Accuracy: **89.09%**
  - Precision: **85.30%**
  - Recall: **94.46%**
  - F1-Score: **89.65%**
  - ROC-AUC: **95.07%**
- **Feature Importance Ranking**:
  1. **Elevation**: **34.77%** (High plateau vs steep southern fault escarpments)
  2. **Lithology**: **25.80%** (Sylhet limestone / Kopili shales vs Precambrian quartzites)
  3. **TWI**: **13.78%** (Severe water accumulation zones)
  4. **Aspect**: **9.77%** (South-facing slopes exposed to monsoon clouds)
  5. **Slope**: **8.76%**
  6. **Curvature**: **7.12%**

### Full-State Susceptibility Breakdown (39,496,161 Pixels)

- **Very Low ($P < 0.20$)**: $27,914,987\text{ px}$ ($70.7\%$)
- **Low ($0.20 \le P < 0.40$)**: $3,764,847\text{ px}$ ($9.5\%$)
- **Moderate ($0.40 \le P < 0.60$)**: $2,430,414\text{ px}$ ($6.2\%$)
- **High ($0.60 \le P < 0.80$)**: $3,007,096\text{ px}$ ($7.6\%$)
- **Very High ($P \ge 0.80$)**: $2,378,817\text{ px}$ ($6.0\%$)

### NASA LHASA Scenario Projections

- **Scenario 1: Dry Pre-Monsoon ($ARI = 1.5\text{ mm}$)**:
  - Safe (Level 0): $94.0\%$ ($37.1\text{M px}$)
  - Advisory (Level 1): $6.0\%$ ($2.4\text{M px}$)
- **Scenario 2: Active Monsoon / Cherrapunji Surge ($ARI = 134.5\text{ mm}$)**:
  - Safe (Level 0): $70.7\%$
  - Warning (Level 3): $7.6\%$ ($3.0\text{M px}$)
  - Severe Emergency (Level 4): $6.0\%$ ($2.4\text{M px}$)
- **Scenario 3: Catastrophic Cloudburst / Escarpment Storm ($ARI = 298.6\text{ mm}$)**:
  - Safe (Level 0): **$0.0\%$**
  - Warning (Level 3): **$6.2\%$** ($2.43\text{M px}$)
  - Severe Emergency (Level 4): **$13.6\%$** ($5.39\text{M px}$)
  - Combined Severe + Warning: **$19.8\%$** under immediate disaster condition

---

## 4. Deliverables & Saved Files

- **Rasters & Layers**:
  - UTM 30m DEM: [`data/processed/dem/meghalaya/utm/meghalaya_dem_utm46n.tif`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/dem/meghalaya/utm/meghalaya_dem_utm46n.tif)
  - Susceptibility GeoTIFF: [`data/processed/results/meghalaya/meghalaya_susceptibility.tif`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_susceptibility.tif)
  - Extreme Alert GeoTIFF: [`data/processed/results/meghalaya/meghalaya_lhasa_alert_extreme.tif`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_lhasa_alert_extreme.tif)
- **Model & Metrics**:
  - XGBoost Model: [`models/meghalaya/meghalaya_xgboost.pkl`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/models/meghalaya/meghalaya_xgboost.pkl)
  - Model JSON Report: [`data/processed/results/meghalaya/meghalaya_model_report.json`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_model_report.json)
  - LHASA JSON Report: [`data/processed/results/meghalaya/meghalaya_lhasa_report.json`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_lhasa_report.json)
- **Maps & Visualizations**:
  - Geology & Events Map: [`data/processed/results/meghalaya/meghalaya_lithology_map.png`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_lithology_map.png)
  - Model Performance Chart: [`data/processed/results/meghalaya/meghalaya_model_performance.png`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_model_performance.png)
  - Susceptibility Map: [`data/processed/results/meghalaya/meghalaya_susceptibility_map.png`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_susceptibility_map.png)
  - LHASA Multi-Scenario Comparison: [`data/processed/results/meghalaya/meghalaya_lhasa_scenario_comparison.png`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_lhasa_scenario_comparison.png)
  - LHASA Operational Alert Map: [`data/processed/results/meghalaya/meghalaya_lhasa_alert_map.png`](file:///c:/Users/Lenovo/Downloads/lhasa_porject/lhasa_porject/data/processed/results/meghalaya/meghalaya_lhasa_alert_map.png)

---

## 5. Detailed Change Log

- **[2026-09-15 00:38 IST]**: Initialized Meghalaya deployment, defined bounding box and confirmed UTM Zone 46N (EPSG:32646).
- **[2026-09-15 00:40 IST]**: Filtered and exported 39 historical events to `data/raw/landslides/meghalaya_events.csv`.
- **[2026-09-15 00:43 IST]**: Downloaded SRTM GL1 30m DEM (42.13 MB) covering entire Shillong Plateau and border escarpments via OpenTopography API.
- **[2026-09-15 00:44 IST]**: Extracted and classified 31 geological units across 6 major lithological groups from USGS dataset.
- **[2026-09-15 00:47 IST]**: Reprojected DEM to 30m UTM 46N ($4,552 \times 9,099$ pixels) and derived Elevation, Slope, Aspect, Curvature, and TWI.
- **[2026-09-15 00:48 IST]**: Applied 150m radial buffer around 39 events, generating 2,979 positive pixels. Built 1:1 balanced dataset (5,958 samples).
- **[2026-09-15 00:49 IST]**: Trained 6-factor XGBoost model. Achieved **94.61% CV AUC** and **95.07% Test AUC**.
- **[2026-09-15 00:52 IST]**: Inferred continuous landslide susceptibility across all 39,496,161 valid terrain pixels. Produced full GeoTIFF and high-resolution PNG map.
- **[2026-09-15 00:53 IST]**: Executed dynamic NASA LHASA nowcast across 3 rainfall scenarios ($ARI = 1.5, 134.5, 298.6\text{ mm}$). Generated extreme alert GeoTIFF, multi-scenario comparison map, and JSON summary report.
- **[2026-09-15 00:54 IST]**: Updated documentation, synchronized all visual artifacts, and verified zero pipeline errors.
