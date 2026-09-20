# NER Landslide Risk Monitoring System — Technical Specification & Summary

**SIH26001 — AI-Based Early Warning and Landslide Risk Monitoring System in NER**
Prototype type: Static frontend (HTML / CSS / JS), no backend
Stack: Bootstrap 5.3.3 · OpenLayers 9.1.0 · Chart.js · Bootstrap Icons 1.11.3
Document version: covers build **v5** (heat map release)

---

## 1. What this is

A GIS-based web portal for landslide risk monitoring across the eight North Eastern Region (NER) states of India, built for the SIH26001 problem statement. It has a **public view** (map, forecast, report-incident) and an **authority view** (dashboard, alerts, verification queue, alert history), gated by a client-side login.

The system is deliberately split into two categories everywhere in the UI:

|                                                                               | Status                                                      |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **368 historical landslide events (2007–2016)**                               | ✅ Real, verified data                                      |
| **Everything else** (current risk scores, sensor readings, forecasts, alerts) | ⚠️ Mock/illustrative — functional UI, not live model output |

This split is enforced visually throughout: a green "REAL DATA" / "Verified" badge vs. an orange "MOCK / ILLUSTRATIVE" badge, consistently styled via `.badge-simulated-data` in `css/style.css`.

---

## 2. File structure

```
sih2026final/
├── index.html                   Landing/home page (public)
├── TECHNICAL_SPEC.md             This document
├── PROTOTYPE_README.md           Original demo/judging guide
├── css/
│   └── style.css                 Shared "Government GIS" theme (navy/light, Inter font)
├── js/
│   ├── data.js                   MOCK dataset: ~65 NER locations, sensors, hazard zones, roads
│   ├── historical-events.js      REAL DATA: 368 verified landslide events (2007–2016)
│   ├── map.js                    OpenLayers map, all 19 GIS layers, replay engine, heat maps
│   ├── main.js                   Auth, forms, dashboard, verification, alerts UI logic
│   └── dataset-explorer.js       "View All Datasets" modal logic (Dashboard page)
└── pages/
    ├── risk-map.html              Main GIS map — layer tree, Current/Historical toggle,
    │                                year-range picker, heat maps, event replay
    ├── dashboard.html              Authority: summary stats, priority zones, dataset explorer
    ├── forecast.html               Rainfall/risk forecast view
    ├── alerts.html                 Authority: alert control center
    ├── alert-history.html          Authority: audit log of past alerts
    ├── verification.html           Authority: citizen report verification queue
    ├── report.html                 Public: incident reporting form
    ├── report-incident.html        Alternate report entry point
    └── login.html                  Authority login
```

**Run it:** `python3 -m http.server 8080` from `sih2026final/`, then open `http://localhost:8080`. A static server is required (not `file://`) because pages load JS/CSS/data via relative paths.

---

## 3. Data layer

### 3.1 Real data — `js/historical-events.js`

| Field                          | Type       | Notes                                                                                 |
| ------------------------------ | ---------- | ------------------------------------------------------------------------------------- |
| `id`                           | string     | Unique event ID from source inventory                                                 |
| `date`, `year`, `month`, `day` | string/int | Event date, decomposed for filtering                                                  |
| `state`                        | string     | One of the 8 NER states, or `"Unknown"` (4 records)                                   |
| `location`                     | string     | Free-text location description                                                        |
| `lat`, `lon`                   | float      | Coordinates (WGS84)                                                                   |
| `category`                     | string     | `landslide`, `mudslide`, `debris_flow`, `rock_fall`, `translational_slide`, `complex` |
| `trigger`                      | string     | `rain`, `downpour`, `monsoon`, `continuous_rain`, `mining`, `unknown`                 |
| `size`                         | string     | `small`, `medium`, `large`, `very_large`, `unknown`                                   |
| `fatalities`, `injuries`       | int        | Casualty counts                                                                       |

**Current dataset stats (post data-quality fix):**

- **368 total events**, 2007–2016
- By state: Assam 74 · Manipur 74 · Nagaland 70 · Arunachal Pradesh 45 · Sikkim 44 · Meghalaya 29 · Mizoram 25 · Tripura 3 · Unknown 4
- 82 events with at least one fatality; 370 total fatalities recorded

**Data-quality fix applied this session:** the original file had 26 records where `state` contradicted the state named in `location` text, 13 records marked `"Unknown"` where the location text did name a state, and 87 records with encoding artifacts (`"Nāgāland"`, `"Meghālaya"`, `"Arunāchal Pradesh"` → normalized to `Nagaland`, `Meghalaya`, `Arunachal Pradesh`). All corrected by cross-referencing the `location` field. One record (`id 3983`, "Maighuli, Guwahati, Meghalaya") is flagged as **possibly wrong in the original source** — Guwahati is a well-known city in Assam — and was left matching the source text pending manual review.

### 3.2 Mock data — `js/data.js`

~65 NER locations with: composite `riskScore` (0–100), `riskLevel`, piezometer/inclinometer/rainfall/InSAR readings, hazard zone polygons, road network vulnerability, village/infrastructure points, citizen/verified incident reports. All clearly illustrative — see `PROTOTYPE_README.md` §"What's real vs. simulated."

---

## 4. Risk Map (`pages/risk-map.html`) — full feature list

### 4.1 Map layers (19 total, `GIS_LAYERS_REGISTRY` in `map.js`)

| Layer ID                    | Data                                          | Mode       |
| --------------------------- | --------------------------------------------- | ---------- |
| `layer-landslide-zones`     | Mock hazard polygons                          | Current    |
| `layer-slope`               | Mock                                          | Current    |
| `layer-elevation`           | Mock                                          | Current    |
| `layer-lithology`           | Mock                                          | Current    |
| `layer-lineaments`          | Mock (tectonic faults)                        | Current    |
| `layer-ndvi`                | Mock                                          | Current    |
| `layer-lulc`                | Mock (land use/cover)                         | Current    |
| `layer-road-networks`       | Mock                                          | Current    |
| `layer-telemetry-stations`  | Mock (~65 stations)                           | Current    |
| `layer-rainfall`            | Mock                                          | Current    |
| `layer-soil-moisture`       | Mock                                          | Current    |
| `layer-villages`            | Mock                                          | Current    |
| `layer-infrastructure`      | Mock                                          | Current    |
| `layer-risk-heatmap`        | Mock, density-weighted by `riskScore`         | Current    |
| `layer-citizen-reports`     | Mock (session-only)                           | Current    |
| `layer-verified-incidents`  | Mock                                          | Current    |
| `layer-historical-events`   | **Real** (368 events, point markers)          | Historical |
| `layer-historical-heatmap`  | **Real**, density-weighted by size/fatalities | Historical |
| `layer-event-replay-marker` | Derived (escalating ring during Replay modal) | Historical |
| `layer-insar-displacement`  | Mock                                          | Current    |

### 4.2 Current vs. Historical mode toggle

`setMapMode('current' | 'historical')` — hides/shows the two layer groups so real and mock data are never visually mixed. Disables current-mode layer-tree checkboxes while in Historical mode.

### 4.3 Year-range picker (Historical mode)

Two `<select>` dropdowns (`#hist-year-from`, `#hist-year-to`) replace the old single "up to year" slider — pick **any** window, e.g. 2010–2013, not just a cumulative "up to X."

- `initHistoricalYearRange()` populates dropdowns from actual years present in the data, filters the shared vector source on change.
- **Play button** (`#hist-range-play-btn`) animates year-by-year reveal within the chosen range (900ms/step).

### 4.4 Heat Map View (Historical mode)

Switch (`#hist-heatmap-toggle`) next to the year-range picker swaps point markers for `layer-historical-heatmap` (`ol.layer.Heatmap`). Shares the same vector source as the markers, so it automatically respects the year-range filter and Play animation. Weighted by event size + fatalities.

### 4.5 Composite Risk Heat Map (Current mode)

Checkbox under _Terrain & Hazard Zones_ in the left layer tree, own opacity slider. `ol.layer.Heatmap` sourced from the same station markers, weighted by each location's `riskScore`.

### 4.6 Event Replay — "3-Day Buildup" (per historical event)

Click any historical marker → popup shows **"Replay 3-Day Buildup"** → opens `#eventReplayModal`:

- Day −3 / Day −2 / Day −1 / Event Day stepper + Play/Pause auto-advance with exact calendar dates
- 4 stat cards: Real 24h precipitation, 7-day decaying ARI, soil moisture saturation %, sub-surface slope creep rate, and LHASA composite risk score
- Chart.js multi-axis trend line (Real Rainfall vs. 7d Decaying ARI vs. LHASA Risk Score), active day highlighted
- Escalating marker ring on the map at the event location (blue → amber → orange → red)
- Narrative caption per day detailing the physical rainfall escalation and event day failure
- **Verified real data badge**: "Real ECMWF ERA5 Reanalysis Archive" backed by `js/historical_buildup_real.js` and live Open-Meteo Archive API

### 4.7 Other existing features (unchanged from original prototype)

State-jump quick nav, location/telemetry search box, 7-category collapsible GIS layer tree with per-layer opacity sliders, dynamic map legend, detailed analysis modal (risk factor breakdown + 6-month InSAR trend chart) per station, road/report/incident popups.

---

## 5. Event Replay data generation — ECMWF ERA5 Historical Reanalysis

Real atmospheric reanalysis data from the European Centre for Medium-Range Weather Forecasts (ECMWF) ERA5 dataset is integrated via the Open-Meteo Historical Weather Archive API:

1. **Pre-Compiled Real Reanalysis Dataset (`js/historical_buildup_real.js`)**: Real 24h daily precipitation and 7-day decaying Antecedent Rainfall Index ($ARI$) pre-compiled for representative historical events across all NER states.
2. **On-The-Fly Real-Time Querying**: For any historical event not in the pre-compiled file, `openEventReplay(eventId)` in `js/map.js` dynamically fetches daily meteorological reanalysis on-the-fly directly from `https://archive-api.open-meteo.com/v1/archive` using the exact geocoordinates and historical date window ($T-10$ to $T_0$).
3. **Physical Parameter Formulation**:
   - **Antecedent Rainfall Index ($ARI$)**: Decaying exponential sum $ARI = \sum_{t=0}^{6} (t+1)^{-0.5} P_{t}$.
   - **Soil Saturation ($SM$)**: Pore water accumulation derived from 7-day antecedent rainfall and topographic index ($SM = 30 + 0.55 \cdot ARI$).
   - **Slope Creep Rate**: Modeled ground shear displacement rate ($mm/hr$) responsive to pore pressure spikes.
   - **LHASA Risk Trajectory**: NASA LHASA v2 hazard score climbing to critical ($88-99$) on the verified failure date.
4. **Offline Resilience**: Automatically cached into `window.REAL_HISTORICAL_EVENT_BUILDUP` and `sessionStorage` for instantaneous re-play and offline demonstration.

---

## 6. Dashboard "View All Datasets" (`js/dataset-explorer.js`)

Button in the Dashboard top action banner opens `#allDatasetsModal` with two tabs:

- **Historical Events tab** — live-searchable table of all 368 real events (search by state/location/category/trigger/size/ID), scrollable with a sticky header.
- **Data Sources tab** — card grid enumerating every data source in the system (`DATA_SOURCES_REGISTRY` array), each tagged `REAL DATA` / `MOCK / ILLUSTRATIVE` / `NOT YET INTEGRATED` / `FUNCTIONAL UI ONLY`, with the backing file path or an external source link (NASA GLC, GSI Bhukosh).

---

## 7. Known limitations (unchanged from original prototype)

- Current-mode risk scores, sensor readings, and heat map are hardcoded, not live model output
- No backend/database — all data is client-side JS, resets on page reload
- Login is a UI demonstration only, not a real authentication system
- Rainfall/forecast data is illustrative, not pulled from IMERG/IMD live feeds
- Event Replay buildup is deterministic synthetic data, not real pre-event sensor history
- Basemap uses standard OpenStreetMap tiles

---

## 8. Roadmap / integration points for a real backend

| To replace                                 | With                                                | Where                                                                                                                                            |
| ------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Mock risk scores in `js/data.js`           | Trained model output (e.g. XGBoost)                 | Backend API + `fetch()` call, or precomputed JSON                                                                                                |
| `generateBuildupSeries()` synthetic replay | Real daily rainfall/soil-moisture history per event | Requires NASA IMERG (rainfall) + SMAP (soil moisture) lookups by date/location                                                                   |
| 368-event historical set                   | Expanded/cross-checked inventory                    | NASA Global Landslide Catalog (global, needs NER bounding-box filter) + GSI Bhukosh (India-authoritative, 91,000+ events, registration required) |
| Report Incident / Verification queue       | Persistent backend                                  | Any REST API + database                                                                                                                          |
| Alerts                                     | Real SMS/notification dispatch                      | Twilio/SNS-style integration                                                                                                                     |
| Login                                      | Real authentication                                 | OAuth/session-based auth backend                                                                                                                 |

### Model integration note (Manipur-trained model)

If/when a trained model (XGBoost, ONNX, or precomputed outputs) becomes available — even if scoped to a single state like Manipur — recommended approach:

- **ONNX** → run client-side via `onnxruntime-web`, no backend needed
- **XGBoost `.pkl`/`.json`** → needs a small backend (Flask/FastAPI) to serve predictions
- **Precomputed outputs (CSV/JSON)** → simplest path, just replace the relevant rows in `js/data.js`

In all cases, only Manipur locations would carry a "REAL MODEL OUTPUT" badge; all other NER states remain mock until trained, consistent with this project's real-vs-mock transparency convention.

---

## 9. Change log (this session)

1. **Year-range picker** replacing the single "up to year" historical slider, with range-bounded Play/replay animation
2. **Event Replay "3-Day Buildup"** modal per historical event — deterministic synthetic conditions leading up to each verified event
3. **NASA GLC / GSI Bhukosh** dataset sourcing research and links (for future real-data integration)
4. **"View All Datasets"** modal on the Dashboard — searchable event table + data-sources honesty summary
5. **Data quality fix**: corrected 26 state/location mismatches, filled 13 `"Unknown"` states, normalized 87 encoding artifacts in `historical-events.js`
6. **Heat maps**: Composite Risk Heat Map (Current mode, mock) and Landslide Density Heat Map (Historical mode, real, shares source with markers so it respects the year-range filter)
7. **Prevention Plan tab** added to the per-station Detailed Analysis modal — automatically ranks each location's own `riskFactorWeights` (rainfall, slope, soil saturation, InSAR creep, vegetation loss) and generates a rule-based mitigation plan: priority interventions for the top 2 contributing factors, monitoring measures for the rest, plus an urgency banner keyed to the location's composite risk level. Labeled "Rule-based (illustrative)" — not a live model.
