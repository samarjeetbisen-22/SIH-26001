# NER Landslide Risk Monitoring System — Prototype README

### SIH26001 — AI-Based Early Warning and Landslide Risk Monitoring System in NER

This package is the frontend prototype for the college-round demo, packaged as a static site (HTML/CSS/JS, Bootstrap 5 + OpenLayers 9).

---

## How to run it

You can run the prototype with either the **full AI Backend API server** (recommended — executes live 30m XGBoost models and Open-Meteo weather telemetry) or any static web server:

### Option A: Full ML Backend Server (Recommended)

```bash
python scripts/api_server.py --port 8080
```

This loads all 4 trained XGBoost models (Sikkim, Nagaland, Meghalaya, Assam) into memory, enables live REST inference at `/api/predict`, fetches real-time meteorological feeds, and serves the web portal.

### Option B: Static File Server (Offline Fallback)

```bash
cd sih2026final_v6
python -m http.server 8080
```

_(When running statically without Python, the frontend automatically hydrates from the validated precomputed model cache in `js/model_predictions_cache.json`.)_

Then open **http://localhost:8080** in Chrome or Edge.

---

## What's real vs. simulated — read this before demoing

| Component                                                                  | Status                        | Details                                                                                                                                                        |
| -------------------------------------------------------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **30m XGBoost Susceptibility Models** (Sikkim, Nagaland, Meghalaya, Assam) | ✅ **Real ML Output**         | 6-factor models trained on empirical inventories achieving 93.6%–95.2% ROC-AUC. Connected via live Python backend (`/api/predict`) and precomputed cache.      |
| **NASA LHASA v2 Dynamic Nowcast**                                          | ✅ **Real Pipeline**          | 7-day decaying Antecedent Rainfall Index ($ARI$) coupled with 30m susceptibility terrain distributions to classify dynamic Hazard Levels 0 to 4.               |
| **Real-Time Meteorological Feeds** (Forecast & Risk Map)                   | ✅ **Real Telemetry**         | High-resolution precipitation history and 72h forecasts queried live from Open-Meteo across all 8 NER states.                                                  |
| **Historical Records layer** (Risk Map → "Historical Records" mode)        | ✅ **Real Data**              | 368 verified landslide events across all 8 NER states, 2007–2016, from cleaned public inventory dataset. Includes real dates, locations, triggers, casualties. |
| **3-Day Buildup Event Replay**                                             | ✅ **Real Data (ECMWF ERA5)** | Real atmospheric reanalysis archive for verified historical landslides.                                                                                        |
| **Current Risk Monitoring layer** (Risk Map → default mode)                | ✅ **Hybrid Model Output**    | Overwriting former mock values with real XGBoost probabilities, physical pore pressures ($\mu = \rho_w \cdot g \cdot h_w$), and empirical creep rates.         |
| **Dashboard, Alerts, Alert History, Verification pages**                   | ✅ **Connected API**          | Real-time triage, multi-channel regional SMS & offline geo-fenced CAP-CP v1.2 alerts, with disk-backed persistence.                                            |

---

## File structure

```
sih2026final/
├── index.html                  Landing/home page (public)
├── css/
│   └── style.css                Shared "Government GIS" theme — navy/light palette, custom components
├── js/
│   ├── data.js                  Mock dataset: ~65 NER locations, sensor readings, hazard zones, roads, faults
│   ├── historical-events.js     REAL DATA: 368 verified landslide events (2007-2016), parsed from CSV
│   ├── map.js                   OpenLayers map init, all GIS layers, mode toggle logic, popups
│   └── main.js                  UI interactivity: auth, forms, dashboard, verification, alerts
└── pages/
    ├── risk-map.html             Main GIS map — layer tree, Current vs Historical mode toggle, year slider
    ├── dashboard.html            Authority-only: summary stats, priority zones
    ├── forecast.html             Rainfall/risk forecast view
    ├── alerts.html                Authority-only: alert control center
    ├── alert-history.html        Authority-only: audit log of past alerts
    ├── verification.html         Authority-only: citizen report verification queue
    ├── report.html                Public: incident reporting form
    ├── report-incident.html      (placeholder/alternate report entry point)
    └── login.html                 Authority login
```

---

## Key feature: Current vs. Historical data mode (Risk Map page)

The risk map has a toggle bar at the top with two modes, kept deliberately separate so real and simulated data are never visually mixed:

- **Current Risk Monitoring** (default) — shows all live/model-output layers: hazard zones, slope, rainfall, soil moisture, lithology, roads, sensors, citizen/verified reports, InSAR.
- **Historical Records** — hides all of the above, shows _only_ the 368 real events, and reveals a **year slider (2007–2016)**. Dragging the slider redraws the map to show only events up to that year — a live "replay" of 10 years of real NER landslide history.

This toggle is the strongest demo moment in the prototype — it's real data, genuinely interactive, and directly answers "how do we know this approach works" without needing to explain accuracy statistics verbally.

---

## Integrated Architecture (Current State)

- **Live ML Model Execution**: The backend (`scripts/api_server.py`) executes 4 real 30m XGBoost models (Sikkim, Nagaland, Meghalaya, Assam) with 93.6%–95.2% ROC-AUC.
- **Dynamic Weather Integration**: Real-time Open-Meteo precipitation feeds and 7-day decaying Antecedent Rainfall Index (ARI) update automatically across all 8 NER states.
- **Dual Persistent Storage**: Reports, authority verifications, audit logs, and dispatched alerts are persistently stored in backend JSON databases (`data/processed/results/`) and synchronized with browser `localStorage`.
- **Dynamic Map Canvas**: OpenLayers vector layers refresh dynamically on user submissions and verifications without page reload.
- **Dual-Mode Offline Fallback**: The frontend automatically detects if the Python server is offline and seamlessly hydrates from the precomputed model cache (`js/model_predictions_cache.json`).

---

## Suggested demo flow

1. **Start ML Backend**: Run `python scripts/api_server.py --port 8080`.
2. **Home Page (`index.html`)**: Point out the live status indicator: `ML Backend Live (4 Models)`.
3. **Risk Map (`pages/risk-map.html`)**: Click stations (e.g. Gangtok, Kohima) to inspect real XGBoost susceptibility probability and physical pore water pressures.
4. **Historical Mode**: Switch toggle to "Historical Records" and drag the year slider (2007–2016) across 368 verified landslide events.
5. **Forecast Page (`pages/forecast.html`)**: Show live rainfall telemetry and dynamic NASA LHASA nowcast hazard distribution.
6. **Incident Reporting & Triage**: Submit a report on `pages/report.html`, observe it dynamically appear on the GIS map, and verify it in `pages/verification.html`.
7. **Emergency Alerts (`pages/alerts.html`)**: Dispatch a regional multi-lingual alert (Nepali, Nagamese, Khasi, Assamese, Hindi, English) with geo-fenced radius and review the immutable log in `pages/alert-history.html`.
