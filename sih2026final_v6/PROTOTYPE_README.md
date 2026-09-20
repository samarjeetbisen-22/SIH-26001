# NER Landslide Risk Monitoring System — Prototype README
### SIH26001 — AI-Based Early Warning and Landslide Risk Monitoring System in NER

This package is the frontend prototype for the college-round demo, packaged as a static site (HTML/CSS/JS, Bootstrap 5 + OpenLayers 9).

---

## How to run it

You need a local web server (not just double-clicking `index.html`) because the pages load JS/CSS/data files via relative paths.

```bash
cd sih2026final
python3 -m http.server 8080
```

Then open **http://localhost:8080** in Chrome or Edge.

(Any static server works — VS Code's "Live Server" extension, `npx serve`, etc. — `python3 -m http.server` is just the simplest option with no install.)

---

## What's real vs. simulated — read this before demoing

This is the single most important thing to know before recording your video or presenting to judges. Being upfront about this split builds credibility; overclaiming and getting caught in Q&A damages it.

| Component | Status | Details |
|---|---|---|
| **Historical Records layer** (Risk Map → "Historical Records" mode) | ✅ **Real data** | 368 verified landslide events across all 8 NER states, 2007–2016, from a cleaned public inventory dataset. Includes real dates, locations, triggers, severity, casualties. |
| **Current Risk Monitoring layer** (Risk Map → default mode) | ⚠️ **Mock/illustrative data** | Risk scores, sensor readings (piezometer, inclinometer), InSAR displacement, and advisories for ~65 NER locations in `js/data.js` are realistic-looking placeholder values, not live model output. |
| **Dashboard, Alerts, Alert History, Forecast, Verification pages** | ⚠️ **Mock/illustrative data** | Built on the same simulated dataset — functional UI, not connected to a live pipeline yet. |
| **Login / role-based access** | ✅ **Functional** | Real client-side logic switching between Public and Authority views — not connected to a real backend/auth system. |
| **Report Incident form** | ✅ **Functional UI** | Captures input and stores it in-session; not persisted to a real database yet. |

**Recommended honest framing for judges:** *"Our Historical Records layer uses 368 real, verified NER landslide events to validate our approach. Our Current Risk Monitoring layer demonstrates the intended UI/UX and output format — we're actively training the underlying XGBoost model on this same real data to replace the illustrative values before the next round."*

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
- **Historical Records** — hides all of the above, shows *only* the 368 real events, and reveals a **year slider (2007–2016)**. Dragging the slider redraws the map to show only events up to that year — a live "replay" of 10 years of real NER landslide history.

This toggle is the strongest demo moment in the prototype — it's real data, genuinely interactive, and directly answers "how do we know this approach works" without needing to explain accuracy statistics verbally.

---

## Known limitations (be upfront about these if asked)

- Risk scores in Current mode are hardcoded, not computed by a live model
- No backend/database — all data is client-side JS, resets on page reload
- Login is a UI demonstration only, not a real authentication system
- Rainfall/forecast data is illustrative, not pulled from IMERG/IMD live feeds yet
- Basemap uses standard OpenStreetMap tiles (switched from CARTO, which now requires a paid API key for anonymous basemap access)

---

## Suggested demo video flow

1. **Home page** — brief pan, state the problem
2. **Risk Map, Current mode** — show the layer tree, click a location (e.g. Tawang), show the risk panel and 7-factor breakdown
3. **Risk Map, switch to Historical mode** — drag the year slider from 2007 → 2016, narrate: *"These are 368 real, verified landslide events across NER — not simulated"*
4. **Click a few real historical markers** — show real dates/locations/casualties in the popup
5. **Dashboard / Forecast / Alerts** — quick pass through the rest of the authority-side flow
6. Close on the roadmap: what's mock today vs. what becomes real model output next

---

## Next steps for later rounds

- Replace `js/data.js` mock risk scores with real XGBoost model output (see the separate Training Data Guide and SQLite database package for the model-side pipeline)
- Connect Report Incident form and Verification queue to a real backend/database
- Wire Alerts to an actual SMS/notification service
- Pull live rainfall (IMERG) and soil moisture (SMAP) instead of static mock values
