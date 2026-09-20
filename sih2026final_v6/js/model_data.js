/**
 * NER Landslide System — Real ML Pipeline Output
 * Auto-derived from trained XGBoost models + NASA LHASA v2 nowcast
 * States complete: Sikkim, Nagaland, Meghalaya, Assam (4/8)
 */

const LHASA_MODEL_METRICS = [
  {
    state: "Sikkim",
    stateKey: "sikkim",
    events: 172,
    eventType: "Polygon inventory (ISRO)",
    gridSize: "~3M px @ 30m",
    crs: "EPSG:32645",
    cvAUC: 93.63,
    testAUC: 93.80,
    accuracy: 86.16,
    f1: 86.48,
    recall: null,
    topFeature: "Lithology",
    topFeaturePct: 25.2,
    featureImportance: { lithology: 25.2, elevation: 19.4, slope: 17.7, aspect: 17.3, curvature: 12.5, twi: 8.0 },
    status: "complete",
    modelFile: "models/trained_model_sikkim_6factors.pkl"
  },
  {
    state: "Nagaland",
    stateKey: "nagaland",
    events: 101,
    eventType: "Point inventory (150m buffer)",
    gridSize: "40M px @ 30m",
    crs: "EPSG:32646",
    cvAUC: 93.35,
    testAUC: 93.63,
    accuracy: 87.86,
    f1: 88.68,
    recall: 95.1,
    topFeature: "Lithology",
    topFeaturePct: 41.3,
    featureImportance: { lithology: 41.3, elevation: 25.7, twi: 12.1, slope: 7.7, aspect: 8.1, curvature: 5.1 },
    status: "complete",
    modelFile: "models/nagaland/nagaland_xgboost.pkl"
  },
  {
    state: "Meghalaya",
    stateKey: "meghalaya",
    events: 39,
    eventType: "Point inventory (150m buffer)",
    gridSize: "41M px @ 30m",
    crs: "EPSG:32646",
    cvAUC: 94.61,
    testAUC: 95.07,
    accuracy: 89.09,
    f1: 89.65,
    recall: 94.46,
    topFeature: "Elevation",
    topFeaturePct: 34.8,
    featureImportance: { elevation: 34.8, lithology: 25.8, twi: 13.8, curvature: 10.3, aspect: 9.3, slope: 6.0 },
    status: "complete",
    modelFile: "models/meghalaya/meghalaya_xgboost.pkl"
  },
  {
    state: "Assam",
    stateKey: "assam",
    events: 105,
    eventType: "Point inventory (150m buffer)",
    gridSize: "305M px @ 30m",
    crs: "EPSG:32646",
    cvAUC: 95.28,
    testAUC: 95.18,
    accuracy: 89.59,
    f1: 90.16,
    recall: 95.4,
    topFeature: "TWI",
    topFeaturePct: 29.1,
    featureImportance: { twi: 29.1, slope: 26.2, lithology: 18.8, elevation: 16.2, curvature: 5.2, aspect: 4.6 },
    status: "complete",
    modelFile: "models/assam/assam_xgboost.pkl"
  },
  { state: "Manipur",    stateKey: "manipur",    status: "pending", events: null },
  { state: "Arunachal Pradesh", stateKey: "arunachal", status: "pending", events: null },
  { state: "Mizoram",   stateKey: "mizoram",    status: "pending", events: null },
  { state: "Tripura",   stateKey: "tripura",    status: "pending", events: null }
];

const LHASA_NOWCAST_RESULTS = {
  sikkim: {
    scenarios: {
      dry:     { label: "Dry (Pre-Monsoon)",          ari: 2.1,   l0: 96.5, l1: 3.5,  l2: 0,    l3: 0,    l4: 0 },
      monsoon: { label: "Active Monsoon",              ari: 98.4,  l0: 87.7, l1: 0,    l2: 0,    l3: 0,    l4: 12.3 },
      extreme: { label: "Extreme Storm (Disaster)",   ari: 232.9, l0: 0,    l1: 87.7, l2: 0,    l3: 0,    l4: 12.3 }
    },
    extremeContext: "Catastrophic cloudburst over Teesta valley"
  },
  nagaland: {
    scenarios: {
      dry:     { label: "Dry (Pre-Monsoon)",             ari: 1.8,   l0: 97.2, l1: 2.8,  l2: 0,    l3: 0,    l4: 0 },
      monsoon: { label: "Active Monsoon (NH-29)",        ari: 92.1,  l0: 62.9, l1: 12.5, l2: 10.1, l3: 10.1, l4: 4.4 },
      extreme: { label: "Extreme Storm (NH-29 Cloudburst)", ari: 193.3, l0: 0, l1: 62.9, l2: 12.5, l3: 10.1, l4: 14.4 }
    },
    extremeContext: "NH-29 / NH-2 Cloudburst — road closure risk"
  },
  meghalaya: {
    scenarios: {
      dry:     { label: "Dry (Pre-Monsoon)",            ari: 2.3,   l0: 97.1, l1: 2.9,  l2: 0,    l3: 0,    l4: 0 },
      monsoon: { label: "Active Monsoon (Cherrapunji)", ari: 145.2, l0: 80.3, l1: 0,    l2: 0,    l3: 6.2,  l4: 13.6 },
      extreme: { label: "Extreme Storm (World-Record Rainfall)", ari: 298.6, l0: 0, l1: 80.3, l2: 0, l3: 6.2, l4: 13.6 }
    },
    extremeContext: "Cherrapunji / Mawsynram world-record rainfall belt"
  },
  assam: {
    scenarios: {
      dry:     { label: "Dry (Pre-Monsoon)",               ari: 2.7,   l0: 96.9, l1: 3.1,  l2: 0,   l3: 0,   l4: 0 },
      monsoon: { label: "Active Monsoon (Brahmaputra)",    ari: 118.3, l0: 82.4, l1: 5.9,  l2: 4.3, l3: 4.3, l4: 3.1 },
      extreme: { label: "Extreme Storm (Dima Hasao Cloudburst)", ari: 212.1, l0: 0, l1: 82.4, l2: 5.9, l3: 4.3, l4: 7.4 }
    },
    extremeContext: "Dima Hasao hills cloudburst — Barak Valley & NH-27 at risk"
  }
};

const LHASA_SUSCEPTIBILITY_CLASSES = {
  sikkim:   { veryLow: 42.1, low: 21.3, moderate: 18.2, high: 11.5, veryHigh: 6.9 },
  nagaland: { veryLow: 38.2, low: 18.5, moderate: 17.0, high: 15.4, veryHigh: 10.9 },
  meghalaya:{ veryLow: 45.6, low: 16.2, moderate: 14.8, high: 13.8, veryHigh: 9.6 },
  assam:    { veryLow: 82.4, low: 5.9,  moderate: 4.3,  high: 4.3,  veryHigh: 3.1 }
};

// Susceptibility PNG overlay bounds [minLon, minLat, maxLon, maxLat] in WGS84
const SUSC_OVERLAY_BOUNDS = {
  "sikkim": {
    "label": "Sikkim", "png": "../images/susceptibility/sikkim_susceptibility.png",
    "extent_wgs84": [88.0699, 27.1924, 88.8057, 27.5528],
    "events": 172, "test_auc_pct": 93.8
  },
  "nagaland": {
    "label": "Nagaland", "png": "../images/susceptibility/nagaland_susceptibility.png",
    "extent_wgs84": [93.492, 25.0843, 95.2359, 27.0163],
    "events": 101, "test_auc_pct": 93.63
  },
  "meghalaya": {
    "label": "Meghalaya", "png": "../images/susceptibility/meghalaya_susceptibility.png",
    "extent_wgs84": [89.8689, 24.968, 92.6041, 26.2329],
    "events": 39, "test_auc_pct": 95.07
  },
  "assam": {
    "label": "Assam", "png": "../images/susceptibility/assam_susceptibility.png",
    "extent_wgs84": [88.8619, 23.9477, 95.0698, 28.0584],
    "events": 105, "test_auc_pct": 95.18
  }
};

// Map location IDs to state keys for ML badge lookup
const LOCATION_STATE_MAP = {
  "loc-gangtok":  "sikkim",
  "loc-kohima":   "nagaland",
  "loc-shillong": "meghalaya",
  "loc-guwahati": "assam",
  "loc-silchar":  "assam",
  "loc-haflong":  "assam",
  "loc-dimapur":  "nagaland"
};

window.LHASA_MODEL_METRICS       = LHASA_MODEL_METRICS;
window.LHASA_NOWCAST_RESULTS      = LHASA_NOWCAST_RESULTS;
window.LHASA_SUSCEPTIBILITY_CLASSES = LHASA_SUSCEPTIBILITY_CLASSES;
window.SUSC_OVERLAY_BOUNDS        = SUSC_OVERLAY_BOUNDS;
window.LOCATION_STATE_MAP         = LOCATION_STATE_MAP;

