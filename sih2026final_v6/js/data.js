/**
 * NER Landslide Risk Monitoring System
 * Mock GIS Dataset, Vulnerable Roads & Emergency Priorities (Part 7 Extended)
 */

const NE_LOCATIONS_DATA = [
  {
    id: "loc-tawang",
    name: "Tawang",
    state: "Arunachal Pradesh",
    district: "Tawang District",
    lat: 27.5861,
    lon: 91.8594,
    elevation: "3,048 m",
    riskScore: 88,
    riskLevel: "Severe",
    rainfall24h: 142.5,
    rainfall7d: 384.2,
    soilMoisture: 89,
    slopeAngle: 42,
    geologyLithology: "Weathered Mica Schist & Gneiss Formations",
    insarDisplacement: "-14.2 mm/yr (Downward Subsidence)",
    vulnerabilityIndex: "High (0.88)",
    activeSensors: 12,
    lastUpdate: "10 mins ago",
    advisory: "CRITICAL: High landslide probability along Sela Pass road corridor. Heavy precipitation expected to continue for 18 hours. Traffic restrictions recommended.",
    evacuationStatus: "Standby Warning Issued",
    emergencyContact: "+91 3794-222221 (DC Tawang Control Room)",
    historicalIncidents: "14 incidents in last 3 years (Major 2024 Sela Slip)",
    sensorReadings: { piezometer: "42.1 kPa (High pore pressure)", inclinometer: "4.2 mm/hr creep displacement", rainGauge: "142.5 mm/24h" },
    riskFactorWeights: { rainfall: 35, slope: 25, soilMoisture: 20, insarCreep: 12, vegetationLoss: 8 },
    insarTrendData: [0.0, -1.8, -4.2, -7.5, -11.0, -14.2]
  },
  {
    id: "loc-guwahati",
    name: "Guwahati",
    state: "Assam",
    district: "Kamrup Metropolitan",
    lat: 26.1445,
    lon: 91.7362,
    elevation: "55 m",
    riskScore: 22,
    riskLevel: "Low",
    rainfall24h: 18.2,
    rainfall7d: 46.0,
    soilMoisture: 38,
    slopeAngle: 12,
    geologyLithology: "Alluvial Silt & Precambrian Granitic Basement",
    insarDisplacement: "-0.5 mm/yr (Stable Terrain)",
    vulnerabilityIndex: "Low (0.22)",
    activeSensors: 24,
    lastUpdate: "5 mins ago",
    advisory: "NORMAL: Slope stability index within safe limits. Routine monitoring active in Narakasur and Kharghuli hill pockets.",
    evacuationStatus: "No Warning Active",
    emergencyContact: "+91 361-2237219 (Assam State Disaster Mgmt Authority)",
    historicalIncidents: "2 minor urban slope slips in 2025",
    sensorReadings: { piezometer: "8.5 kPa (Normal)", inclinometer: "0.1 mm/hr", rainGauge: "18.2 mm/24h" },
    riskFactorWeights: { rainfall: 15, slope: 10, soilMoisture: 12, insarCreep: 3, vegetationLoss: 5 },
    insarTrendData: [0.0, -0.1, -0.2, -0.3, -0.4, -0.5],
    mlModel: { stateKey: "assam", cvAUC: 95.28, testAUC: 95.18, accuracy: 89.59, topFeature: "TWI (29%)", lhasaExtremeL4pct: 7.4, lhasaExtremeARI: 212.1, suscHighVeryHighPct: 7.4, isRealData: true }
  },
  {
    id: "loc-shillong",
    name: "Shillong",
    state: "Meghalaya",
    district: "East Khasi Hills",
    lat: 25.5788,
    lon: 91.8933,
    elevation: "1,525 m",
    riskScore: 76,
    riskLevel: "High",
    rainfall24h: 98.4,
    rainfall7d: 265.1,
    soilMoisture: 79,
    slopeAngle: 36,
    geologyLithology: "Shillong Group Quartzites & Fractured Sandstone",
    insarDisplacement: "-8.6 mm/yr (Moderate Creep)",
    vulnerabilityIndex: "High (0.76)",
    activeSensors: 18,
    lastUpdate: "8 mins ago",
    advisory: "WARNING: Saturated soil conditions along NH-6 Shillong-Jowai route. Increased risk of debris flow near upper Shillong peak slopes.",
    evacuationStatus: "Advisory Level 2",
    emergencyContact: "+91 364-2225289 (Meghalaya SDMA)",
    historicalIncidents: "9 incidents recorded in last monsoons",
    sensorReadings: { piezometer: "28.4 kPa (Elevated)", inclinometer: "1.8 mm/hr creep", rainGauge: "98.4 mm/24h" },
    riskFactorWeights: { rainfall: 32, slope: 22, soilMoisture: 22, insarCreep: 14, vegetationLoss: 10 },
    insarTrendData: [0.0, -1.2, -2.8, -4.5, -6.9, -8.6],
    mlModel: { stateKey: "meghalaya", cvAUC: 94.61, testAUC: 95.07, accuracy: 89.09, topFeature: "Elevation (35%)", lhasaExtremeL4pct: 13.6, lhasaExtremeARI: 298.6, suscHighVeryHighPct: 23.4, isRealData: true }
  },
  {
    id: "loc-aizawl",
    name: "Aizawl",
    state: "Mizoram",
    district: "Aizawl District",
    lat: 23.7271,
    lon: 92.7176,
    elevation: "1,132 m",
    riskScore: 91,
    riskLevel: "Severe",
    rainfall24h: 168.0,
    rainfall7d: 412.5,
    soilMoisture: 94,
    slopeAngle: 48,
    geologyLithology: "Surma Group Interbedded Sandstone & Shale",
    insarDisplacement: "-18.5 mm/yr (Rapid Surface Deformation)",
    vulnerabilityIndex: "Severe (0.91)",
    activeSensors: 16,
    lastUpdate: "2 mins ago",
    advisory: "ALERT: Critical slope instability on Hunthar & Laipuitlang ridges. Mass movement telemetry threshold breached. Immediate evacuation recommended for lower hill slope settlements.",
    evacuationStatus: "ACTIVE EVACUATION NOTICE",
    emergencyContact: "+91 389-2335892 (Mizoram Disaster Mgmt)",
    historicalIncidents: "22 severe landslides recorded (Major 2013 Laipuitlang disaster)",
    sensorReadings: { piezometer: "56.8 kPa (CRITICAL)", inclinometer: "6.5 mm/hr active slip", rainGauge: "168.0 mm/24h" },
    riskFactorWeights: { rainfall: 38, slope: 28, soilMoisture: 24, insarCreep: 18, vegetationLoss: 12 },
    insarTrendData: [0.0, -2.5, -5.8, -10.1, -14.5, -18.5]
  },
  {
    id: "loc-imphal",
    name: "Imphal",
    state: "Manipur",
    district: "Imphal West",
    lat: 24.8170,
    lon: 93.9368,
    elevation: "786 m",
    riskScore: 48,
    riskLevel: "Moderate",
    rainfall24h: 42.1,
    rainfall7d: 115.0,
    soilMoisture: 54,
    slopeAngle: 24,
    geologyLithology: "Disang Formation Mudstone & Siltstone",
    insarDisplacement: "-3.2 mm/yr (Minor Settlement)",
    vulnerabilityIndex: "Moderate (0.48)",
    activeSensors: 14,
    lastUpdate: "15 mins ago",
    advisory: "WATCH: Moderate soil moisture accumulation along Imphal-Jiribam national highway (NH-37). Maintenance crews deployed.",
    evacuationStatus: "Monitored Watch",
    emergencyContact: "+91 385-2443441 (Manipur Relief & Rehabilitation)",
    historicalIncidents: "5 highway slope blockages in 2025",
    sensorReadings: { piezometer: "14.2 kPa (Moderate)", inclinometer: "0.4 mm/hr", rainGauge: "42.1 mm/24h" },
    riskFactorWeights: { rainfall: 20, slope: 16, soilMoisture: 18, insarCreep: 6, vegetationLoss: 8 },
    insarTrendData: [0.0, -0.4, -1.0, -1.8, -2.5, -3.2]
  },
  {
    id: "loc-kohima",
    name: "Kohima",
    state: "Nagaland",
    district: "Kohima District",
    lat: 25.6751,
    lon: 94.1086,
    elevation: "1,444 m",
    riskScore: 79,
    riskLevel: "High",
    rainfall24h: 110.6,
    rainfall7d: 290.4,
    soilMoisture: 82,
    slopeAngle: 38,
    geologyLithology: "Highly Sheared Disang Shales & Flysch Deposits",
    insarDisplacement: "-11.2 mm/yr (Active Subsidence)",
    vulnerabilityIndex: "High (0.79)",
    activeSensors: 15,
    lastUpdate: "6 mins ago",
    advisory: "HIGH RISK: Active sinking zone telemetry around Dzüvürü and Phesama bypass corridor. Heavy vehicles re-routed.",
    evacuationStatus: "High Alert Issued",
    emergencyContact: "+91 370-2291122 (Nagaland NSDMA)",
    historicalIncidents: "11 major subsidence events",
    sensorReadings: { piezometer: "32.6 kPa (High)", inclinometer: "2.4 mm/hr displacement", rainGauge: "110.6 mm/24h" },
    riskFactorWeights: { rainfall: 30, slope: 24, soilMoisture: 20, insarCreep: 15, vegetationLoss: 10 },
    insarTrendData: [0.0, -1.5, -3.4, -5.9, -8.7, -11.2],
    mlModel: { stateKey: "nagaland", cvAUC: 93.35, testAUC: 93.63, accuracy: 87.86, topFeature: "Lithology (41%)", lhasaExtremeL4pct: 14.4, lhasaExtremeARI: 193.3, suscHighVeryHighPct: 26.3, isRealData: true }
  },
  {
    id: "loc-gangtok",
    name: "Gangtok",
    state: "Sikkim",
    district: "East Sikkim",
    lat: 27.3389,
    lon: 88.6065,
    elevation: "1,650 m",
    riskScore: 85,
    riskLevel: "Severe",
    rainfall24h: 136.2,
    rainfall7d: 358.0,
    soilMoisture: 88,
    slopeAngle: 44,
    geologyLithology: "Daling Group Chlorite-Schist & Phyllites",
    insarDisplacement: "-15.8 mm/yr (High Rockfall Instability)",
    vulnerabilityIndex: "Severe (0.85)",
    activeSensors: 21,
    lastUpdate: "3 mins ago",
    advisory: "CRITICAL: Accelerated rock movement on NH-10 Gangtok-Siliguri lifeline corridor near Dikchu and 9th Mile. Travelers advised to avoid night travel.",
    evacuationStatus: "Stage 2 Travel Advisory",
    emergencyContact: "+91 3592-202461 (Sikkim SSDMA)",
    historicalIncidents: "18 major rockfalls & slips",
    sensorReadings: { piezometer: "48.3 kPa (CRITICAL)", inclinometer: "5.1 mm/hr movement", rainGauge: "136.2 mm/24h" },
    riskFactorWeights: { rainfall: 36, slope: 26, soilMoisture: 22, insarCreep: 16, vegetationLoss: 10 },
    insarTrendData: [0.0, -2.1, -5.0, -8.6, -12.3, -15.8],
    mlModel: { stateKey: "sikkim", cvAUC: 93.63, testAUC: 93.80, accuracy: 86.16, topFeature: "Lithology (25%)", lhasaExtremeL4pct: 12.3, lhasaExtremeARI: 232.9, suscHighVeryHighPct: 18.4, isRealData: true }
  },
  {
    id: "loc-agartala",
    name: "Agartala",
    state: "Tripura",
    district: "West Tripura",
    lat: 23.8315,
    lon: 91.2868,
    elevation: "12 m",
    riskScore: 18,
    riskLevel: "Low",
    rainfall24h: 14.5,
    rainfall7d: 38.0,
    soilMoisture: 32,
    slopeAngle: 8,
    geologyLithology: "Recent Alluvium & Unconsolidated Sand",
    insarDisplacement: "-0.2 mm/yr (Stable Plain)",
    vulnerabilityIndex: "Very Low (0.18)",
    activeSensors: 10,
    lastUpdate: "20 mins ago",
    advisory: "CLEAR: Low terrain relief with stable soil conditions. River discharge levels normal.",
    evacuationStatus: "Normal Operational State",
    emergencyContact: "+91 381-2416045 (Tripura Emergency Control)",
    historicalIncidents: "No landslide incidents reported",
    sensorReadings: { piezometer: "5.0 kPa (Stable)", inclinometer: "0.0 mm/hr", rainGauge: "14.5 mm/24h" },
    riskFactorWeights: { rainfall: 12, slope: 8, soilMoisture: 10, insarCreep: 2, vegetationLoss: 4 },
    insarTrendData: [0.0, -0.0, -0.1, -0.1, -0.2, -0.2],
    hasPredefinedData: true,
    rainfallFactor: "Low",
    soilMoistureFactor: "Low",
    slopeFactor: "Low",
    historicalFactor: "Low"
  },
  {
    id: "loc-haflong",
    name: "Haflong",
    state: "Assam",
    district: "Dima Hasao District",
    lat: 25.1685,
    lon: 93.0163,
    elevation: "680 m",
    riskScore: 84,
    riskLevel: "Severe",
    rainfall24h: 128.4,
    rainfall7d: 310.2,
    soilMoisture: 86,
    slopeAngle: 39,
    geologyLithology: "Surma Group Sandstone & Shales (High TWI Saturated Slopes)",
    insarDisplacement: "-14.2 mm/yr (Active Slope Sinking)",
    vulnerabilityIndex: "Severe (0.84)",
    activeSensors: 19,
    lastUpdate: "4 mins ago",
    advisory: "CRITICAL: Heavy rainfall triggering slope instability along NH-27 hill section and Lumding-Badarpur railway cutting. High risk of debris flows in Jatinga valley.",
    evacuationStatus: "Stage 2 Flood & Landslide Watch",
    emergencyContact: "+91 3673-236222 (Dima Hasao DDMA)",
    historicalIncidents: "16 major rail/road landslides in 2022-2025",
    sensorReadings: { piezometer: "44.5 kPa (Critical)", inclinometer: "4.8 mm/hr", rainGauge: "128.4 mm/24h" },
    riskFactorWeights: { rainfall: 35, slope: 25, soilMoisture: 22, insarCreep: 10, vegetationLoss: 8 },
    insarTrendData: [0.0, -1.8, -4.2, -7.5, -11.0, -14.2],
    mlModel: { stateKey: "assam", cvAUC: 95.28, testAUC: 95.18, accuracy: 89.59, topFeature: "TWI (29.1%)", lhasaExtremeL4pct: 7.4, lhasaExtremeARI: 212.1, suscHighVeryHighPct: 7.4, isRealData: true }
  },
  {
    id: "loc-dimapur",
    name: "Dimapur",
    state: "Nagaland",
    district: "Dimapur District",
    lat: 25.9060,
    lon: 93.7270,
    elevation: "145 m",
    riskScore: 52,
    riskLevel: "Moderate",
    rainfall24h: 48.0,
    rainfall7d: 135.0,
    soilMoisture: 58,
    slopeAngle: 18,
    geologyLithology: "Tipam Sandstone & Alluvial Terrace Deposit",
    insarDisplacement: "-2.4 mm/yr (Minor Settlement)",
    vulnerabilityIndex: "Moderate (0.52)",
    activeSensors: 12,
    lastUpdate: "12 mins ago",
    advisory: "WATCH: Moderate rainfall accumulating on foothills. NH-29 gateway corridor clear with monitored drainage.",
    evacuationStatus: "Routine Monitoring",
    emergencyContact: "+91 3862-248555 (Dimapur DDMA)",
    historicalIncidents: "4 minor foothill slips near Chumoukedima",
    sensorReadings: { piezometer: "16.8 kPa (Normal)", inclinometer: "0.6 mm/hr", rainGauge: "48.0 mm/24h" },
    riskFactorWeights: { rainfall: 22, slope: 15, soilMoisture: 18, insarCreep: 5, vegetationLoss: 5 },
    insarTrendData: [0.0, -0.3, -0.7, -1.2, -1.8, -2.4],
    mlModel: { stateKey: "nagaland", cvAUC: 93.35, testAUC: 93.63, accuracy: 87.86, topFeature: "Lithology (41.3%)", lhasaExtremeL4pct: 14.4, lhasaExtremeARI: 193.3, suscHighVeryHighPct: 26.3, isRealData: true }
  }
];

// Locations without predefined landslide risk data (Prototype Low Risk / Clear status)
const UNLISTED_LOCATIONS_DATA = [
  { id: "loc-silchar", name: "Silchar", state: "Assam", district: "Cachar District", lat: 24.8333, lon: 92.7789, hasPredefinedData: false },
  { id: "loc-dibrugarh", name: "Dibrugarh", state: "Assam", district: "Dibrugarh District", lat: 27.4728, lon: 94.9120, hasPredefinedData: false },
  { id: "loc-tezpur", name: "Tezpur", state: "Assam", district: "Sonitpur District", lat: 26.6528, lon: 92.7926, hasPredefinedData: false },
  { id: "loc-jorhat", name: "Jorhat", state: "Assam", district: "Jorhat District", lat: 26.7509, lon: 94.2037, hasPredefinedData: false },
  { id: "loc-itanagar", name: "Itanagar", state: "Arunachal Pradesh", district: "Papum Pare District", lat: 27.0844, lon: 93.6053, hasPredefinedData: false },
  { id: "loc-pasighat", name: "Pasighat", state: "Arunachal Pradesh", district: "East Siang District", lat: 28.0664, lon: 95.3262, hasPredefinedData: false },
  { id: "loc-diphu", name: "Diphu", state: "Assam", district: "Karbi Anglong District", lat: 25.8456, lon: 93.4320, hasPredefinedData: false },
  { id: "loc-nagaon", name: "Nagaon", state: "Assam", district: "Nagaon District", lat: 26.3473, lon: 92.6841, hasPredefinedData: false }
];

window.NE_LOCATIONS_DATA = NE_LOCATIONS_DATA;
window.UNLISTED_LOCATIONS_DATA = UNLISTED_LOCATIONS_DATA;
window.ALL_SEARCHABLE_LOCATIONS = [...NE_LOCATIONS_DATA, ...UNLISTED_LOCATIONS_DATA];


// GeoJSON Risk Zones
const MOCK_HAZARD_ZONES = [
  { name: "Tawang-Sela Severe Hazard Belt", riskLevel: "Severe", colorHex: "#dc2626", coordinates: [[91.80, 27.62], [91.92, 27.61], [91.90, 27.54], [91.81, 27.55], [91.80, 27.62]] },
  { name: "Aizawl Ridge Critical Slips", riskLevel: "Severe", colorHex: "#dc2626", coordinates: [[92.68, 23.75], [92.75, 23.76], [92.74, 23.69], [92.67, 23.70], [92.68, 23.75]] },
  { name: "Gangtok-Dikchu Highway Corridor", riskLevel: "Severe", colorHex: "#dc2626", coordinates: [[88.56, 27.37], [88.64, 27.36], [88.63, 27.30], [88.55, 27.31], [88.56, 27.37]] },
  { name: "East Khasi Hills High Susceptibility Belt", riskLevel: "High", colorHex: "#ea580c", coordinates: [[91.83, 25.61], [91.95, 25.60], [91.94, 25.53], [91.82, 25.54], [91.83, 25.61]] },
  { name: "Kohima-Phesama Subsidence Zone", riskLevel: "High", colorHex: "#ea580c", coordinates: [[94.05, 25.70], [94.15, 25.69], [94.14, 25.63], [94.04, 25.64], [94.05, 25.70]] },
  { name: "Imphal West Hill Slopes", riskLevel: "Moderate", colorHex: "#d97706", coordinates: [[93.88, 24.84], [93.98, 24.83], [93.97, 24.78], [93.87, 24.79], [93.88, 24.84]] },
  { name: "Guwahati Plain Alluvial Zone", riskLevel: "Low", colorHex: "#059669", coordinates: [[91.68, 26.18], [91.78, 26.17], [91.77, 26.10], [91.67, 26.11], [91.68, 26.18]] },
  { name: "Agartala Low Relief Terrain", riskLevel: "Low", colorHex: "#059669", coordinates: [[91.23, 23.86], [91.33, 23.85], [91.32, 23.79], [91.22, 23.80], [91.23, 23.86]] }
];

// Mock Slope Gradient Polygons
const MOCK_SLOPE_ZONES = [
  { name: "Sela Pass High Slope (>45° Very Steep)", slopeCategory: "Very Steep (>45°)", colorHex: "#991b1b", coordinates: [[91.82, 27.60], [91.90, 27.59], [91.88, 27.54], [91.81, 27.55], [91.82, 27.60]] },
  { name: "Aizawl Ridge Escarpment (30°-45° Steep)", slopeCategory: "Steep (30°-45°)", colorHex: "#dc2626", coordinates: [[92.69, 23.74], [92.74, 23.75], [92.73, 23.70], [92.68, 23.71], [92.69, 23.74]] },
  { name: "Shillong Plateau Slope (15°-30° Moderate)", slopeCategory: "Moderate (15°-30°)", colorHex: "#d97706", coordinates: [[91.84, 25.59], [91.92, 25.58], [91.91, 25.54], [91.83, 25.55], [91.84, 25.59]] },
  { name: "Guwahati Plain Slope (<15° Low)", slopeCategory: "Low (<15°)", colorHex: "#16a34a", coordinates: [[91.69, 26.16], [91.76, 26.15], [91.75, 26.12], [91.68, 26.13], [91.69, 26.16]] }
];

// Mock Elevation Bands
const MOCK_ELEVATION_ZONES = [
  { band: "3,000 m+ (Alpine High Altitude)", colorHex: "#64748b", coordinates: [[91.78, 27.64], [91.94, 27.63], [91.92, 27.52], [91.76, 27.53], [91.78, 27.64]] },
  { band: "1,500 – 3,000 m (High Hill Belt)", colorHex: "#3b82f6", coordinates: [[88.54, 27.38], [88.66, 27.37], [88.64, 27.28], [88.52, 27.29], [88.54, 27.38]] },
  { band: "500 – 1,500 m (Mid Hill Slope)", colorHex: "#10b981", coordinates: [[94.02, 25.72], [94.18, 25.71], [94.16, 25.61], [94.00, 25.62], [94.02, 25.72]] },
  { band: "0 – 500 m (Lowland River Plain)", colorHex: "#f59e0b", coordinates: [[91.65, 26.20], [91.80, 26.19], [91.78, 26.08], [91.63, 26.09], [91.65, 26.20]] }
];

// Mock Rainfall Telemetry Stations
const MOCK_RAINFALL_STATIONS = [
  { name: "Tawang Telemetry Station", val: 142.5, status: "HIGH", lat: 27.5861, lon: 91.8594, state: "Arunachal" },
  { name: "Shillong Peak Rain Gauge", val: 118.0, status: "HIGH", lat: 25.5788, lon: 91.8933, state: "Meghalaya" },
  { name: "Aizawl Hunthar Met Station", val: 96.0, status: "MODERATE", lat: 23.7271, lon: 92.7176, state: "Mizoram" },
  { name: "Gangtok Dikchu Met Station", val: 110.0, status: "HIGH", lat: 27.3389, lon: 88.6065, state: "Sikkim" },
  { name: "Kohima Phesama Met Station", val: 88.0, status: "MODERATE", lat: 25.6751, lon: 94.1086, state: "Nagaland" },
  { name: "Guwahati Kamrup Met Gauge", val: 42.0, status: "LOW", lat: 26.1445, lon: 91.7362, state: "Assam" },
  { name: "Imphal West Rain Gauge", val: 65.0, status: "MODERATE", lat: 24.8170, lon: 93.9368, state: "Manipur" },
  { name: "Agartala Met Gauge", val: 35.0, status: "LOW", lat: 23.8315, lon: 91.2868, state: "Tripura" }
];

// Mock Soil Moisture Saturation
const MOCK_SOIL_MOISTURE_DATA = [
  { name: "Tawang Sela Sector", val: 89, status: "Saturated", lat: 27.5861, lon: 91.8594 },
  { name: "Shillong Plateau Sector", val: 76, status: "High", lat: 25.5788, lon: 91.8933 },
  { name: "Aizawl Ridge Sector", val: 68, status: "Moderate", lat: 23.7271, lon: 92.7176 },
  { name: "Gangtok Teesta Sector", val: 81, status: "Saturated", lat: 27.3389, lon: 88.6065 },
  { name: "Kohima Sinking Zone", val: 72, status: "High", lat: 25.6751, lon: 94.1086 },
  { name: "Guwahati Drainage Zone", val: 38, status: "Normal", lat: 26.1445, lon: 91.7362 }
];

// Mock Geological Lithology
const MOCK_LITHOLOGY_ZONES = [
  { rockType: "Weathered Schist & Gneiss", stability: "Low / Unstable", colorHex: "#b45309", coordinates: [[91.78, 27.63], [91.94, 27.62], [91.92, 27.52], [91.76, 27.53], [91.78, 27.63]] },
  { rockType: "Shillong Quartzite & Sandstone", stability: "Moderate", colorHex: "#0284c7", coordinates: [[91.82, 25.62], [91.96, 25.61], [91.94, 25.51], [91.80, 25.52], [91.82, 25.62]] },
  { rockType: "Siltstone & Mudstone Shales", stability: "Highly Unstable", colorHex: "#be123c", coordinates: [[92.65, 23.77], [92.77, 23.78], [92.75, 23.68], [92.63, 23.69], [92.65, 23.77]] },
  { rockType: "Alluvial Deposits & Silt Plain", stability: "High / Stable", colorHex: "#15803d", coordinates: [[91.64, 26.20], [91.80, 26.19], [91.78, 26.08], [91.62, 26.09], [91.64, 26.20]] }
];

// Mock Tectonic Fault Lines & Lineaments
const MOCK_LINEAMENTS_DATA = [
  { name: "Main Boundary Thrust (MBT) Sela Fault Line", status: "Active Fault", coords: [[91.70, 27.55], [91.85, 27.58], [92.00, 27.62]] },
  { name: "Dauki Fault System (Shillong Border)", status: "Active Fault", coords: [[91.65, 25.50], [91.85, 25.55], [92.10, 25.60]] },
  { name: "Aizawl Longitudinal Thrust Fracture", status: "Subsurface Lineament", coords: [[92.65, 23.65], [92.72, 23.72], [92.80, 23.80]] },
  { name: "Teesta Megacline Lineament (Sikkim)", status: "Active Lineament", coords: [[88.50, 27.20], [88.60, 27.35], [88.70, 27.50]] }
];

// Mock NDVI Vegetation Cover
const MOCK_NDVI_ZONES = [
  { category: "Dense Vegetation (NDVI > 0.6)", colorHex: "#15803d", coordinates: [[91.75, 27.60], [91.88, 27.59], [91.86, 27.50], [91.73, 27.51], [91.75, 27.60]] },
  { category: "Moderate Vegetation (NDVI 0.3 - 0.6)", colorHex: "#84cc16", coordinates: [[91.81, 25.60], [91.93, 25.59], [91.91, 25.50], [91.79, 25.51], [91.81, 25.60]] },
  { category: "Sparse / Exposed Slope (NDVI < 0.3)", colorHex: "#f59e0b", coordinates: [[92.67, 23.75], [92.76, 23.76], [92.74, 23.68], [92.65, 23.69], [92.67, 23.75]] }
];

// Mock Land Use / Land Cover (LULC)
const MOCK_LULC_ZONES = [
  { type: "Protected Dense Forest", colorHex: "#166534", coordinates: [[91.76, 27.61], [91.90, 27.60], [91.88, 27.51], [91.74, 27.52], [91.76, 27.61]] },
  { type: "Urban & Rural Settlement", colorHex: "#b91c1c", coordinates: [[91.70, 26.17], [91.78, 26.16], [91.76, 26.10], [91.68, 26.11], [91.70, 26.17]] },
  { type: "Terraced Agriculture", colorHex: "#ca8a04", coordinates: [[94.04, 25.70], [94.16, 25.69], [94.14, 25.60], [94.02, 25.61], [94.04, 25.70]] },
  { type: "Exposed Slope / Quarrying", colorHex: "#78716c", coordinates: [[92.66, 23.74], [92.75, 23.75], [92.73, 23.67], [92.64, 23.68], [92.66, 23.74]] }
];

// Mock Village Settlements
const MOCK_VILLAGES_DATA = [
  { name: "Jang Village", pop: "3,200 Residents", exposure: "High Risk", lat: 27.6000, lon: 91.8800 },
  { name: "Kiting Settlement", pop: "1,850 Residents", exposure: "Severe Risk", lat: 27.5600, lon: 91.8400 },
  { name: "Singtam Town", pop: "8,400 Residents", exposure: "Critical Corridor", lat: 27.2300, lon: 88.5000 },
  { name: "Hunthar Settlement", pop: "4,600 Residents", exposure: "Severe Slope Risk", lat: 23.7300, lon: 92.7100 },
  { name: "Phesama Village", pop: "2,900 Residents", exposure: "Sinking Zone", lat: 25.6500, lon: 94.1100 },
  { name: "Upper Shillong Hamlet", pop: "5,100 Residents", exposure: "High Rainfall Risk", lat: 25.5500, lon: 91.8700 }
];

// Mock Critical Infrastructure Assets
const MOCK_CRITICAL_INFRA_DATA = [
  { name: "Sela Tunnel South Portal & Substation", type: "Defense Substation", icon: "⚡", lat: 27.5861, lon: 91.8594 },
  { name: "Civil Hospital West Kameng", type: "Hospital", icon: "🏥", lat: 27.2644, lon: 92.4159 },
  { name: "Teesta Hydel Intake Dam", type: "Hydro Dam", icon: "💧", lat: 27.3389, lon: 88.6065 },
  { name: "Aizawl Ridge Water Mains", type: "Water Facility", icon: "🚰", lat: 23.7271, lon: 92.7176 },
  { name: "Umiam Hydro Substation", type: "Power Grid", icon: "⚡", lat: 25.5788, lon: 91.8933 },
  { name: "Phesama High Voltage Grid Towers", type: "Power Transmission", icon: "📡", lat: 25.6751, lon: 94.1086 }
];

// Mock InSAR Ground Displacement Telemetry
const MOCK_INSAR_DATA = [
  { location: "Tawang Sela Pass Sector", rate: "-14.2 mm/year", category: "Significant Movement", status: "Active Subsidence", lat: 27.5861, lon: 91.8594 },
  { location: "Bomdila Pass Slope", rate: "-8.6 mm/year", category: "Moderate Movement", status: "Creep Slip", lat: 27.2644, lon: 92.4159 },
  { location: "Aizawl Hunthar Ridge", rate: "-18.5 mm/year", category: "Significant Movement", status: "Critical Subsidence", lat: 23.7271, lon: 92.7176 },
  { location: "Gangtok Dikchu Corridor", rate: "-11.4 mm/year", category: "Significant Movement", status: "Debris Slope Slide", lat: 27.3389, lon: 88.6065 },
  { location: "Shillong Peak Slope", rate: "-3.2 mm/year", category: "Stable / Slow Creep", status: "Minor Movement", lat: 25.5788, lon: 91.8933 },
  { location: "Guwahati City Plain", rate: "-0.5 mm/year", category: "Stable", status: "Stable Terrain", lat: 26.1445, lon: 91.7362 }
];


// Mock Vulnerable Road Corridors for OpenLayers Map (Part 7)
const MOCK_VULNERABLE_ROADS = [
  {
    id: "road-nh10",
    name: "NH-10 (Siliguri - Gangtok Lifeline)",
    status: "Blocked / Critical",
    statusCategory: "Red",
    riskScore: 85,
    nearestIncident: "REP-2026-101 (Debris Blockage near Dikchu)",
    affectedVillages: "Singtam, Dikchu, 9th Mile, Ranipool",
    recommendedPriority: "Priority 1 (Emergency Clearance Required)",
    coords: [[88.50, 27.20], [88.56, 27.30], [88.60, 27.34], [88.62, 27.38]]
  },
  {
    id: "road-aizawl-ridge",
    name: "Aizawl Surma Ridge Bypass",
    status: "Blocked / Critical",
    statusCategory: "Red",
    riskScore: 91,
    nearestIncident: "REP-2026-102 (Laipuitlang Longitudinal Crack)",
    affectedVillages: "Hunthar, Laipuitlang, Ramhlun, Durtlang",
    recommendedPriority: "Priority 2 (Immediate Structural Containment)",
    coords: [[92.65, 23.70], [92.70, 23.72], [92.72, 23.75], [92.76, 23.78]]
  },
  {
    id: "road-sela-pass",
    name: "Sela Pass South Approach (NH-13)",
    status: "High Risk",
    statusCategory: "Orange",
    riskScore: 88,
    nearestIncident: "REP-2026-103 (Active Mudflow on Convoy Route)",
    affectedVillages: "Jang, Kiting, Lhou, Lumla",
    recommendedPriority: "Priority 3 (Controlled Military Convoy Only)",
    coords: [[91.80, 27.52], [91.84, 27.56], [91.87, 27.60], [91.92, 27.64]]
  },
  {
    id: "road-phesama",
    name: "Phesama Sinking Bypass (NH-2)",
    status: "High Risk",
    statusCategory: "Orange",
    riskScore: 79,
    nearestIncident: "REP-2026-104 (Phesama Tarmac Buckling)",
    affectedVillages: "Phesama, Dzüvürü, Viswema",
    recommendedPriority: "Priority 4 (Heavy Vehicle Restriction Active)",
    coords: [[94.04, 25.62], [94.08, 25.66], [94.11, 25.68], [94.15, 25.72]]
  },
  {
    id: "road-nh6",
    name: "Shillong - Jowai Highway (NH-6)",
    status: "Potential Risk",
    statusCategory: "Yellow",
    riskScore: 76,
    nearestIncident: "REP-2026-105 (Umiam Sandstone Rockfall)",
    affectedVillages: "Upper Shillong, Elephant Falls, Mylliem",
    recommendedPriority: "Priority 5 (24h Geotechnical Patrol Active)",
    coords: [[91.82, 25.50], [91.86, 25.55], [91.90, 25.58], [91.95, 25.62]]
  },
  {
    id: "road-guwahati-dispur",
    name: "Guwahati - Dispur Feeder Corridor",
    status: "Operational",
    statusCategory: "Green",
    riskScore: 22,
    nearestIncident: "None Reported (Normal Flow)",
    affectedVillages: "Kamrup Urban Plain",
    recommendedPriority: "Priority 6 (Standard Maintenance)",
    coords: [[91.70, 26.10], [91.73, 26.13], [91.76, 26.15], [91.80, 26.17]]
  }
];

// Emergency Response Priority Table Records (Automatic Formula Data)
const EMERGENCY_RESPONSE_PRIORITIES = [
  {
    id: "loc-tawang",
    locationId: "loc-tawang",
    corridorName: "Tawang Road Corridor (NH-13 Sela Pass)",
    state: "Arunachal Pradesh",
    district: "Tawang District",
    lat: 27.5861,
    lon: 91.8594,
    centerCoords: [91.8594, 27.5861],
    riskScore: 88,
    exposureLevel: "High",
    roadImportance: "Critical Corridor / National Highway",
    criticalInfrastructure: "Critical",
    infraDescription: "Sela Tunnel South Portal & Defense Convoy Substation"
  },
  {
    id: "loc-bomdila",
    locationId: "loc-bomdila",
    corridorName: "Bomdila / West Kameng Corridor (NH-229)",
    state: "Arunachal Pradesh",
    district: "West Kameng",
    lat: 27.2644,
    lon: 92.4159,
    centerCoords: [92.4159, 27.2644],
    riskScore: 82,
    exposureLevel: "Medium",
    roadImportance: "Critical Corridor / National Highway",
    criticalInfrastructure: "High",
    infraDescription: "District Grid Transformer Station & Civil Hospital Access"
  },
  {
    id: "loc-shillong",
    locationId: "loc-shillong",
    corridorName: "Shillong Hills Corridor (NH-6 Shillong-Jowai)",
    state: "Meghalaya",
    district: "East Khasi Hills",
    lat: 25.5788,
    lon: 91.8933,
    centerCoords: [91.8933, 25.5788],
    riskScore: 76,
    exposureLevel: "High",
    roadImportance: "State Highway",
    criticalInfrastructure: "High",
    infraDescription: "Umiam Hydro Reservoir Feeder & Shillong Peak Radar"
  },
  {
    id: "loc-aizawl",
    locationId: "loc-aizawl",
    corridorName: "Aizawl Slope Zone (Hunthar Ridge)",
    state: "Mizoram",
    district: "Aizawl District",
    lat: 23.7271,
    lon: 92.7176,
    centerCoords: [92.7176, 23.7271],
    riskScore: 72,
    exposureLevel: "Medium",
    roadImportance: "State Highway",
    criticalInfrastructure: "Medium",
    infraDescription: "Aizawl Water Supply Mains & Ridge Power Line"
  },
  {
    id: "loc-guwahati",
    locationId: "loc-guwahati",
    corridorName: "Guwahati Plain Corridor (Kamrup)",
    state: "Assam",
    district: "Kamrup Metropolitan",
    lat: 26.1445,
    lon: 91.7362,
    centerCoords: [91.7362, 26.1445],
    riskScore: 22,
    exposureLevel: "Low",
    roadImportance: "District Road",
    criticalInfrastructure: "Low",
    infraDescription: "Urban Stormwater Drainage & Local Substation"
  }
];

// Initial Pre-Populated Citizen Field Reports for Prototype Verification Demonstration
const INITIAL_MOCK_REPORTS = [
  {
    id: "REP-2026-001",
    type: "Landslide",
    state: "Arunachal Pradesh",
    locationName: "Tawang Sector 4 (NH-13 Sela Pass)",
    lat: 27.5861,
    lon: 91.8594,
    description: "Rockfall and mudflow debris blocking convoy route near Sela South Portal.",
    reporterName: "Dorjee Norbu",
    reporterContact: "+91 94360 12345",
    submittedAt: "2026-08-26 10:15 IST",
    image: "https://images.unsplash.com/photo-1541675154750-0444c7d51e8e?auto=format&fit=crop&w=400&q=80",
    status: "VERIFIED",
    riskLevel: "Severe",
    authorityRemarks: "Confirmed by BRO Field Inspection Team."
  },
  {
    id: "REP-2026-002",
    type: "Road Blockage",
    state: "Arunachal Pradesh",
    locationName: "Sela South Approach Road",
    lat: 27.5800,
    lon: 91.8500,
    description: "Heavy boulder fall halts traffic flow on military bypass.",
    reporterName: "Tsering Lhamo",
    reporterContact: "+91 94020 98765",
    submittedAt: "2026-08-26 11:30 IST",
    image: "https://images.unsplash.com/photo-1541675154750-0444c7d51e8e?auto=format&fit=crop&w=400&q=80",
    status: "VERIFIED",
    riskLevel: "Severe",
    authorityRemarks: "Verified by District Police Patrol."
  },
  {
    id: "REP-2026-003",
    type: "Crack in Slope",
    state: "Arunachal Pradesh",
    locationName: "Bomdila Pass Sector (NH-229)",
    lat: 27.2644,
    lon: 92.4159,
    description: "Visible tension cracks along road shoulder near West Kameng civil hospital.",
    reporterName: "Pema Khandu",
    reporterContact: "+91 94361 55443",
    submittedAt: "2026-08-26 12:45 IST",
    image: "https://images.unsplash.com/photo-1508873696983-2df515122519?auto=format&fit=crop&w=400&q=80",
    status: "VERIFIED",
    riskLevel: "High",
    authorityRemarks: "Piezometer data confirms active movement."
  },
  {
    id: "REP-2026-004",
    type: "Rockfall",
    state: "Meghalaya",
    locationName: "Shillong Peak Road (NH-6)",
    lat: 25.5788,
    lon: 91.8933,
    description: "Minor rockfall on upper Shillong curve.",
    reporterName: "Sanbor Shullai",
    reporterContact: "+91 98620 11223",
    submittedAt: "2026-08-26 14:00 IST",
    image: "https://images.unsplash.com/photo-1508873696983-2df515122519?auto=format&fit=crop&w=400&q=80",
    status: "PENDING VERIFICATION",
    riskLevel: "High",
    authorityRemarks: ""
  },
  {
    id: "REP-2026-005",
    type: "Ground Movement",
    state: "Mizoram",
    locationName: "Aizawl Hunthar Ridge",
    lat: 23.7271,
    lon: 92.7176,
    description: "Slope subsidence observed near water main line.",
    reporterName: "Lalthanhawla",
    reporterContact: "+91 98623 99887",
    submittedAt: "2026-08-26 15:20 IST",
    image: "https://images.unsplash.com/photo-1541675154750-0444c7d51e8e?auto=format&fit=crop&w=400&q=80",
    status: "PENDING VERIFICATION",
    riskLevel: "High",
    authorityRemarks: ""
  },
  {
    id: "REP-2026-006",
    type: "Flash Flood",
    state: "Assam",
    locationName: "Guwahati Kamrup Sector",
    lat: 26.1445,
    lon: 91.7362,
    description: "Waterlogging along hill drainage channel.",
    reporterName: "Bhaben Sarma",
    reporterContact: "+91 98640 33221",
    submittedAt: "2026-08-26 16:10 IST",
    image: "https://images.unsplash.com/photo-1508873696983-2df515122519?auto=format&fit=crop&w=400&q=80",
    status: "PENDING VERIFICATION",
    riskLevel: "Moderate",
    authorityRemarks: ""
  }
];


// State Coordinates Map
const STATE_VIEW_COORDS = {
  "all": { center: [92.5, 26.0], zoom: 7.2 },
  "arunachal": { center: [91.8594, 27.5861], zoom: 8.5 },
  "assam": { center: [91.7362, 26.1445], zoom: 8.5 },
  "meghalaya": { center: [91.8933, 25.5788], zoom: 8.8 },
  "mizoram": { center: [92.7176, 23.7271], zoom: 8.8 },
  "manipur": { center: [93.9368, 24.8170], zoom: 8.8 },
  "nagaland": { center: [94.1086, 25.6751], zoom: 8.8 },
  "sikkim": { center: [88.6065, 27.3389], zoom: 8.8 },
  "tripura": { center: [91.2868, 23.8315], zoom: 8.8 }
};

// Target Area Metadata Dictionary for Emergency Alert Dispatch
const MOCK_ALERT_AREAS_DATA = {
  "tawang": {
    district: "Tawang District, Arunachal Pradesh",
    riskLevel: "Severe",
    nearbyVillages: "Jang, Kiting, Lhou, Lumla, Mukto (4 Hill Hamlets)",
    affectedRoads: "Sela Pass South Approach Road (NH-13) & Military Convoy Corridor",
    estPopulation: 14850
  },
  "west_kameng": {
    district: "West Kameng District, Arunachal Pradesh",
    riskLevel: "High",
    nearbyVillages: "Dirang, Bomdila, Bhalukpong (3 Sectors)",
    affectedRoads: "Bhalukpong-Bomdila Highway (NH-228)",
    estPopulation: 22400
  },
  "aizawl": {
    district: "Aizawl District, Mizoram",
    riskLevel: "Severe",
    nearbyVillages: "Hunthar, Laipuitlang, Ramhlun, Durtlang (5 Ridge Communities)",
    affectedRoads: "Aizawl Ridge Ring Road & World Bank Bypass",
    estPopulation: 18500
  },
  "shillong": {
    district: "East Khasi Hills, Meghalaya",
    riskLevel: "High",
    nearbyVillages: "Upper Shillong, Elephant Falls, Mylliem, Laitkor",
    affectedRoads: "Shillong-Jowai Lifeline Highway (NH-6)",
    estPopulation: 31200
  },
  "gangtok": {
    district: "East Sikkim, Sikkim",
    riskLevel: "Severe",
    nearbyVillages: "Dikchu, Singtam, 9th Mile, Ranipool",
    affectedRoads: "Gangtok-Siliguri Highway Corridor (NH-10)",
    estPopulation: 42000
  },
  "kohima": {
    district: "Kohima District, Nagaland",
    riskLevel: "High",
    nearbyVillages: "Phesama, Dzüvürü, Viswema, Jakhama",
    affectedRoads: "Kohima-Imphal Sinking Bypass Corridor (NH-2)",
    estPopulation: 19600,
    stateKey: "nagaland"
  },
  "haflong": {
    district: "Dima Hasao District, Assam",
    riskLevel: "Severe",
    nearbyVillages: "Jatinga, Mahur, Harangajao, Lower Haflong (6 Hill Pockets)",
    affectedRoads: "Silchar-Saurashtra East-West Corridor (NH-27) & Lumding-Badarpur Railway",
    estPopulation: 43800,
    stateKey: "assam"
  },
  "guwahati": {
    district: "Kamrup Metropolitan, Assam",
    riskLevel: "Moderate",
    nearbyVillages: "Narakasur Hills, Kharghuli, Kahilipara, Maligaon Slopes",
    affectedRoads: "Guwahati-Shillong Road (GS Road) & Kamakhya Hill Approach",
    estPopulation: 68500,
    stateKey: "assam"
  }
};

// Initial Pre-Populated Emergency Dispatched Alerts
const INITIAL_EMERGENCY_ALERTS = [
  {
    id: "ALT-NER-2026-001",
    timestamp: "2026-09-19 01:15 IST",
    authority: "🤖 NASA LHASA v2 + 30m XGBoost AI Model (Autonomous)",
    targetArea: "Gangtok Urban Belt & NH-10 Corridor (Sikkim)",
    riskLevel: "Severe",
    alertType: "Severe Emergency Alert",
    channels: ["Cell Broadcast (CBS - Offline Handset Push)", "LoRaWAN & VHF Radio Siren Mesh", "Online Multilingual SMS", "CAP-CP NDMA Gateway Push"],
    geoRadiusKm: 15,
    cbsTowers: 8,
    loraGateways: 11,
    language: "nepali",
    langName: "नेपाली (Nepali)",
    modelTriggered: true,
    recipients: 42000,
    status: "DISPATCHED (LIVE SIMULATION)",
    message: "आपतकालीन निर्देशन: अत्यधिक वर्षाका कारण पूर्वी सिक्किमको एनएच-१० र डिक्चु क्षेत्रमा जमिन भासिने र ठूलो पहिरो जाने उच्च जोखिम उत्पन्न भएको छ। भिरालो र जोखिमयुक्त ठाउँबाट तुरुन्त सुरक्षित स्थानमा जानुहोस्।"
  },
  {
    id: "ALT-NER-2026-002",
    timestamp: "2026-09-18 20:30 IST",
    authority: "admin (Senior Operations Officer)",
    targetArea: "Kohima Phesama Sinking Sector (Nagaland)",
    riskLevel: "High",
    alertType: "Warning",
    channels: ["Cell Broadcast (CBS - Offline Handset Push)", "Online Multilingual SMS"],
    geoRadiusKm: 15,
    cbsTowers: 8,
    loraGateways: 11,
    language: "nagamese",
    langName: "Nagamese / English",
    modelTriggered: false,
    recipients: 28000,
    status: "DISPATCHED (LIVE SIMULATION)",
    message: "HOSHIYAR THAKIBI: Bishi borokh pori ase, Kohima NH-29 aru Phesama sinking zone te mati dhori jabo laga bishi risk ase. Gari loi jabo naparibo, safe jaka te thakibi."
  },
  {
    id: "ALT-NER-2026-003",
    timestamp: "2026-09-18 16:45 IST",
    authority: "🤖 30m Real-Time Monitor (Autonomous)",
    targetArea: "Shillong Plateau & NH-6 Route (Meghalaya)",
    riskLevel: "Moderate",
    alertType: "Warning",
    channels: ["Cell Broadcast (CBS - Offline Handset Push)", "Online Multilingual SMS"],
    geoRadiusKm: 25,
    cbsTowers: 18,
    loraGateways: 24,
    language: "khasi",
    langName: "Ka Ktien Khasi (Khasi)",
    modelTriggered: true,
    recipients: 55000,
    status: "DISPATCHED (LIVE SIMULATION)",
    message: "KA JINGMA JUR: Ka jingther u slap ka la pynlong ka jingma kaba khraw ha NH-6 Shillong-Jowai bad ki thain Cherrapunji. Ki paidbah kiba shong ha ki jaka riat ki dei ban phet noh sha ki jaka ba shngain."
  },
  {
    id: "ALT-NER-2026-004",
    timestamp: "2026-09-18 11:20 IST",
    authority: "admin (Senior Operations Officer)",
    targetArea: "Dima Hasao Hills / Haflong (Assam)",
    riskLevel: "Severe",
    alertType: "Road Closure",
    channels: ["Cell Broadcast (CBS - Offline Handset Push)", "LoRaWAN & VHF Radio Siren Mesh", "Online Multilingual SMS"],
    geoRadiusKm: 15,
    cbsTowers: 8,
    loraGateways: 11,
    language: "assamese",
    langName: "অসমীয়া (Assamese)",
    modelTriggered: false,
    recipients: 35000,
    status: "DISPATCHED (LIVE SIMULATION)",
    message: "ভূমিস্খলনৰ সতৰ্কবাৰ্তা: ধাৰাসাৰ বৰষুণৰ বাবে ডিমা হাছাওৰ পাহাৰীয়া এলেকা আৰু এন এইচ-২৭ হাফলং সংযোগী পথত ভূমিস্খলনৰ আশংকা। পাহাৰীয়া পথত সাৱধানে চলাচল কৰক।"
  }
];

// LocalStorage Keys
const LOCAL_STORAGE_REPORTS_KEY = 'NER_LANDSLIDE_USER_REPORTS';
const LOCAL_STORAGE_SESSION_KEY = 'NER_AUTHORITY_SESSION';
const LOCAL_STORAGE_AUDIT_LOG_KEY = 'NER_AUTHORITY_AUDIT_LOG';
const LOCAL_STORAGE_ALERTS_KEY = 'NER_EMERGENCY_ALERTS';

function getStoredAlerts() {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_ALERTS_KEY);
    if (!raw) {
      localStorage.setItem(LOCAL_STORAGE_ALERTS_KEY, JSON.stringify(INITIAL_EMERGENCY_ALERTS));
      return INITIAL_EMERGENCY_ALERTS;
    }
    return JSON.parse(raw);
  } catch (e) {
    return INITIAL_EMERGENCY_ALERTS;
  }
}

function saveNewAlert(newAlert) {
  try {
    const existing = getStoredAlerts();
    existing.unshift(newAlert);
    localStorage.setItem(LOCAL_STORAGE_ALERTS_KEY, JSON.stringify(existing));
    return true;
  } catch (e) {
    return false;
  }
}

function getStoredReports() {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_REPORTS_KEY);
    if (!raw) {
      localStorage.setItem(LOCAL_STORAGE_REPORTS_KEY, JSON.stringify(INITIAL_MOCK_REPORTS));
      return INITIAL_MOCK_REPORTS;
    }
    return JSON.parse(raw);
  } catch (e) {
    return INITIAL_MOCK_REPORTS;
  }
}


function saveNewReport(newReport) {
  try {
    const existing = getStoredReports();
    existing.unshift(newReport);
    localStorage.setItem(LOCAL_STORAGE_REPORTS_KEY, JSON.stringify(existing));
    return true;
  } catch (e) {
    return false;
  }
}

function updateReportStatus(reportId, newStatus, remarks = "") {
  try {
    const existing = getStoredReports();
    const target = existing.find(r => r.id === reportId);
    if (target) {
      target.status = newStatus;
      if (remarks) target.authorityRemarks = remarks;
      localStorage.setItem(LOCAL_STORAGE_REPORTS_KEY, JSON.stringify(existing));
      
      if (window.appendAuditLog) {
        window.appendAuditLog(newStatus, reportId, remarks);
      }
      return true;
    }
    return false;
  } catch (e) {
    return false;
  }
}

function getAuditLogs() {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_AUDIT_LOG_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch (e) {
    return [];
  }
}

function appendAuditLog(action, reportId, remarks = "") {
  try {
    const logs = getAuditLogs();
    const session = getAuthoritySession();
    const officer = session ? `${session.user} (${session.role})` : "admin (Authority Officer)";
    const now = new Date();
    const timeStr = `${now.toISOString().slice(0, 10)} ${now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;

    const newLog = {
      id: `LOG-${Math.floor(1000 + Math.random() * 9000)}`,
      authority: officer,
      action: action,
      reportId: reportId,
      timestamp: timeStr,
      remarks: remarks || "Status updated in central system."
    };

    logs.unshift(newLog);
    localStorage.setItem(LOCAL_STORAGE_AUDIT_LOG_KEY, JSON.stringify(logs));
    return newLog;
  } catch (e) {
    return null;
  }
}

function getAuthoritySession() {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_SESSION_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

function setAuthoritySession(username = 'admin') {
  const sessionObj = {
    loggedIn: true,
    user: username,
    role: "NDMA Senior Operations Officer",
    token: `AUTH-2026-${Math.floor(100000 + Math.random() * 900000)}`,
    loginTime: new Date().toISOString()
  };
  localStorage.setItem(LOCAL_STORAGE_SESSION_KEY, JSON.stringify(sessionObj));
  return sessionObj;
}

function clearAuthoritySession() {
  localStorage.removeItem(LOCAL_STORAGE_SESSION_KEY);
}

// Explicit Window Exports for Global Accessibility Across All Modules
window.NE_LOCATIONS_DATA = typeof NE_LOCATIONS_DATA !== 'undefined' ? NE_LOCATIONS_DATA : [];
window.EMERGENCY_RESPONSE_PRIORITIES = typeof EMERGENCY_RESPONSE_PRIORITIES !== 'undefined' ? EMERGENCY_RESPONSE_PRIORITIES : [];
window.INITIAL_MOCK_REPORTS = typeof INITIAL_MOCK_REPORTS !== 'undefined' ? INITIAL_MOCK_REPORTS : [];
window.getStoredReports = getStoredReports;
window.saveNewReport = saveNewReport;
window.updateReportStatus = updateReportStatus;
window.getAuditLogs = getAuditLogs;
window.appendAuditLog = appendAuditLog;
window.getAuthoritySession = getAuthoritySession;
window.setAuthoritySession = setAuthoritySession;
window.clearAuthoritySession = clearAuthoritySession;
window.getStoredAlerts = getStoredAlerts;
window.saveNewAlert = saveNewAlert;
window.MOCK_HAZARD_ZONES = typeof MOCK_HAZARD_ZONES !== 'undefined' ? MOCK_HAZARD_ZONES : [];
window.MOCK_SLOPE_ZONES = typeof MOCK_SLOPE_ZONES !== 'undefined' ? MOCK_SLOPE_ZONES : [];
window.MOCK_ELEVATION_ZONES = typeof MOCK_ELEVATION_ZONES !== 'undefined' ? MOCK_ELEVATION_ZONES : [];
window.MOCK_RAINFALL_STATIONS = typeof MOCK_RAINFALL_STATIONS !== 'undefined' ? MOCK_RAINFALL_STATIONS : [];
window.MOCK_SOIL_MOISTURE_DATA = typeof MOCK_SOIL_MOISTURE_DATA !== 'undefined' ? MOCK_SOIL_MOISTURE_DATA : [];
window.MOCK_LITHOLOGY_ZONES = typeof MOCK_LITHOLOGY_ZONES !== 'undefined' ? MOCK_LITHOLOGY_ZONES : [];
window.MOCK_LINEAMENTS_DATA = typeof MOCK_LINEAMENTS_DATA !== 'undefined' ? MOCK_LINEAMENTS_DATA : [];
window.MOCK_NDVI_ZONES = typeof MOCK_NDVI_ZONES !== 'undefined' ? MOCK_NDVI_ZONES : [];
window.MOCK_LULC_ZONES = typeof MOCK_LULC_ZONES !== 'undefined' ? MOCK_LULC_ZONES : [];
window.MOCK_VILLAGES_DATA = typeof MOCK_VILLAGES_DATA !== 'undefined' ? MOCK_VILLAGES_DATA : [];
window.MOCK_CRITICAL_INFRA_DATA = typeof MOCK_CRITICAL_INFRA_DATA !== 'undefined' ? MOCK_CRITICAL_INFRA_DATA : [];
window.MOCK_INSAR_DATA = typeof MOCK_INSAR_DATA !== 'undefined' ? MOCK_INSAR_DATA : [];
window.MOCK_VULNERABLE_ROADS = typeof MOCK_VULNERABLE_ROADS !== 'undefined' ? MOCK_VULNERABLE_ROADS : [];


