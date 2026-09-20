# Pan-NER Landslide Pipeline — Master Deployment Status

**Region:** North-East India (NER) — 8 States  
**Pipeline:** 30m DEM + XGBoost 6-Factor Susceptibility + NASA LHASA v2 Nowcast  
**Last Updated:** 2026-09-15

---

## Regional Overview

| State             | Events         | Status          | CV AUC     | Test AUC   | Accuracy   | Top Feature     | Extreme Storm L3+L4                 |
| ----------------- | -------------- | --------------- | ---------- | ---------- | ---------- | --------------- | ----------------------------------- |
| Sikkim            | 172 polygons   | ✅ Complete     | 93.63%     | 93.80%     | 86.16%     | Lithology 25.2% | 12.3% L4 (ARI=232.9mm)              |
| Nagaland          | 101 points     | ✅ Complete     | 93.35%     | 93.63%     | 87.86%     | Lithology 41.3% | 14.4% L4 + 10.1% L3 (ARI=193.3mm)   |
| Meghalaya         | 39 points      | ✅ Complete     | 94.61%     | 95.07%     | 89.09%     | Elevation 34.8% | 13.6% L4 + 6.2% L3 (ARI=298.6mm)    |
| **Assam**         | **105 points** | **✅ Complete** | **95.28%** | **95.18%** | **89.59%** | **TWI 29.1%**   | **7.4% L4 + 4.3% L3 (ARI=212.1mm)** |
| Manipur           | TBD            | ⬜ Pending      | —          | —          | —          | —               | —                                   |
| Arunachal Pradesh | TBD            | ⬜ Pending      | —          | —          | —          | —               | —                                   |
| Mizoram           | TBD            | ⬜ Pending      | —          | —          | —          | —               | —                                   |
| Tripura           | TBD            | ⬜ Pending      | —          | —          | —          | —               | —                                   |

**4 of 8 states complete.**

---

## Completed State Details

### ✅ Sikkim (Baseline Model)

- **DEM:** 30m UTM Zone 45N (EPSG:32645)
- **Events:** 172 ISRO polygon inventory → 3,112 positive pixels
- **Grid:** ~3,000,725 valid pixels
- **Model:** CV AUC 93.63% | Test AUC 93.80% | Acc 86.16% | F1 86.48%
- **Feature rank:** Lithology > Elevation > Slope > Aspect > Curvature > TWI
- **LHASA:** Disaster storm (ARI=232.9mm) → 12.3% Level 4 Severe
- **Status doc:** _(integrated into main project notes)_

---

### ✅ Nagaland

- **DEM:** SRTM GL1 30m, UTM Zone 46N (EPSG:32646), 7,075 × 5,742
- **Events:** 101 points → 7,494 positive pixels (150m buffer)
- **Training:** 14,988 balanced samples
- **Model:** CV AUC 93.35% | Test AUC 93.63% | Acc 87.86% | Recall 95.1%
- **Feature rank:** Lithology 41.3% > Elevation 25.7% > TWI 12.1% > Slope 7.7%
- **LHASA:** Extreme (ARI=193.3mm) → 14.4% L4 + 10.1% L3 = **24.5% combined**
- **Status doc:** `MEGHALAYA_DEPLOYMENT_STATUS.md` (combined)

---

### ✅ Meghalaya

- **DEM:** SRTM GL1 30m, UTM Zone 46N (EPSG:32646), 4,552 × 9,099
- **Events:** 39 points → 2,979 positive pixels (150m buffer)
- **Training:** 5,958 balanced samples
- **Model:** CV AUC 94.61% | Test AUC **95.07%** | Acc 89.09% | Recall 94.46%
- **Feature rank:** Elevation 34.8% > Lithology 25.8% > TWI 13.8%
- **LHASA:** Extreme (ARI=298.6mm, world-record rainfall belt) → 13.6% L4 + 6.2% L3 = **19.8%**
- **Status doc:** `MEGHALAYA_DEPLOYMENT_STATUS.md`

---

### ✅ Assam

- **DEM:** Copernicus 30m (11 tiles), UTM Zone 46N (EPSG:32646), 14,982 × 20,351
- **Events:** 105 points → 8,116 positive pixels (150m buffer)
- **Training:** 16,232 balanced samples
- **Model:** CV AUC **95.28%** | Test AUC **95.18%** | Acc 89.59% | Recall 95.4%
- **Feature rank:** TWI 29.1% > Slope 26.2% > Lithology 18.8% > Elevation 16.2%
- **Unique insight:** TWI dominance reflects Brahmaputra valley saturation-driven failures
- **LHASA:** Extreme Dima Hasao cloudburst (ARI=212.1mm) → 7.4% L4 + 4.3% L3 = **11.7%**
- **Status doc:** `ASSAM_DEPLOYMENT_STATUS.md`

---

## Pending States

### ⬜ Manipur

- **Priority:** Next after Assam
- **Key corridors:** NH-37, NH-102 (Imphal–Jiribam)
- **Rainfall regime:** 1,500–2,500 mm/year; intense pre-monsoon storms
- **DEM plan:** Copernicus 30m tiles (N23–N25, E093–E095)
- **Estimated tiles:** ~6 tiles

### ⬜ Arunachal Pradesh

- **Priority:** 3rd (largest state, highest relief)
- **Key corridors:** Siang, Kameng, Lohit river valleys; Tawang
- **DEM plan:** Multiple Copernicus tiles (~20+ tiles for full state)
- **Challenge:** Large area (83,743 km²), cloud cover

### ⬜ Mizoram

- **Priority:** 4th
- **Key corridors:** NH-306 (Aizawl–Silchar), Tlawng River valley
- **Rainfall:** 2,500–3,000 mm/year

### ⬜ Tripura

- **Priority:** 5th (smallest, mostly plains)
- **Key corridors:** Gomati valley, Dhalai district
- **Rainfall:** 2,000–2,500 mm/year

---

## Cross-State Comparison: Feature Importance

| Feature   | Sikkim | Nagaland  | Meghalaya | Assam     |
| --------- | ------ | --------- | --------- | --------- |
| Lithology | 25.2%  | **41.3%** | 25.8%     | 18.8%     |
| Elevation | 19.4%  | 25.7%     | **34.8%** | 16.2%     |
| Slope     | 17.7%  | 7.7%      | 6.0%      | **26.2%** |
| TWI       | 8.0%   | 12.1%     | 13.8%     | **29.1%** |
| Aspect    | 17.3%  | 8.1%      | 9.3%      | 4.6%      |
| Curvature | 12.5%  | 5.1%      | 10.3%     | 5.2%      |

**Key insight:** Each state has a geomorphically distinct dominant driver — geology controls in Nagaland, relief energy in Meghalaya, wetness/drainage in Assam.

---

## LHASA Nowcast Comparison (Extreme Storms)

| State     | ARI (mm) | L4 Severe | L3 Warning | Combined  |
| --------- | -------- | --------- | ---------- | --------- |
| Sikkim    | 232.9    | 12.3%     | —          | 12.3%     |
| Nagaland  | 193.3    | 14.4%     | 10.1%      | **24.5%** |
| Meghalaya | 298.6    | 13.6%     | 6.2%       | 19.8%     |
| Assam     | 212.1    | 7.4%      | 4.3%       | 11.7%     |

**Nagaland has the highest combined L3+L4 exposure** (24.5%) — concentrated along NH-29/NH-2 narrow mountain corridors where the entire road network falls in high susceptibility zones.

---

## Change Log

| Date       | Change                                                                            |
| ---------- | --------------------------------------------------------------------------------- |
| 2026-09-13 | Sikkim baseline model complete (CV AUC 93.63%)                                    |
| 2026-09-14 | Pan-NER inventory analysis — 507 events across 8 states                           |
| 2026-09-14 | Pan-NER lithology extracted — 316 geological units (USGS)                         |
| 2026-09-14 | Nagaland pipeline complete — CV AUC 93.35%, LHASA extreme 24.5% L3+L4             |
| 2026-09-14 | Meghalaya pipeline complete — CV AUC 94.61%, Test AUC 95.07%, LHASA extreme 19.8% |
| 2026-09-15 | Assam pipeline complete — CV AUC 95.28%, Test AUC 95.18%, LHASA extreme 11.7%     |
| 2026-09-15 | **Next:** Manipur pipeline deployment                                             |
