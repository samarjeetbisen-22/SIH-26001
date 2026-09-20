"""
Fetch Real-Time Rainfall Telemetry & Compute NASA LHASA v2 Nowcast
States: Sikkim, Nagaland, Meghalaya, Assam (4 States Operational)
Source: Open-Meteo API (High-Resolution Global Reanalysis & Forecast, No Auth Required)
"""

import urllib.request
import json
import numpy as np

# Exact weights from scripts/lhasa_engine.py: w_t = (t + 1)^(-0.5)
ARI_WEIGHTS = [(t + 1) ** (-0.5) for t in range(7)]

# Susceptibility distributions (% of land area) from 30m XGBoost inference
STATE_SUSC_DISTRIBUTION = {
    "sikkim":    {"vlow": 42.1, "low": 21.3, "mod": 18.2, "high": 11.5, "vhigh": 6.9},
    "nagaland":  {"vlow": 38.2, "low": 18.5, "mod": 17.0, "high": 15.4, "vhigh": 10.9},
    "meghalaya": {"vlow": 45.6, "low": 16.2, "mod": 14.8, "high": 13.8, "vhigh": 9.6},
    "assam":     {"vlow": 82.4, "low": 5.9,  "mod": 4.3,  "high": 4.3,  "vhigh": 3.1}
}

MONITORED_STATES = {
    "sikkim": {
        "name": "Sikkim",
        "station": "Gangtok (East Sikkim)",
        "lat": 27.3389,
        "lon": 88.6065,
        "corridor": "NH-10 Gangtok–Siliguri lifeline corridor"
    },
    "nagaland": {
        "name": "Nagaland",
        "station": "Kohima (Dzüvürü Corridor)",
        "lat": 25.6751,
        "lon": 94.1086,
        "corridor": "NH-29 Kohima–Dimapur bypass & Phesama sinking zone"
    },
    "meghalaya": {
        "name": "Meghalaya",
        "station": "Shillong (East Khasi Hills)",
        "lat": 25.5788,
        "lon": 91.8933,
        "corridor": "NH-6 Shillong–Jowai route & Cherrapunji escarpment"
    },
    "assam": {
        "name": "Assam",
        "station": "Dima Hasao / Haflong Hills",
        "lat": 25.1685,
        "lon": 93.0163,
        "corridor": "NH-27 Haflong section & Lumding–Badarpur railway"
    }
}

def fetch_state_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&past_days=7&forecast_days=1&timezone=Asia%2FKolkata"
    req = urllib.request.Request(url, headers={"User-Agent": "NER-Landslide-System/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    return data.get("daily", {})

def compute_lhasa_percentages(susc, ari):
    """
    Computes percentage of land in Level 0 (Safe) through Level 4 (Severe)
    given susceptibility distribution and Antecedent Rainfall Index (ARI).
    Thresholds:
      Low:       ARI < 40 mm
      Moderate:  40 <= ARI < 80 mm
      Heavy:     80 <= ARI < 140 mm
      Extreme:   ARI >= 140 mm
    """
    vl = susc["vlow"]
    lo = susc["low"]
    mo = susc["mod"]
    hi = susc["high"]
    vh = susc["vhigh"]

    l0 = l1 = l2 = l3 = l4 = 0.0

    if ari < 40.0: # Low Rain
        l0 = vl + lo + mo + hi
        l1 = vh
    elif ari < 80.0: # Moderate Rain
        l0 = vl + lo
        l1 = mo
        l2 = hi
        l3 = vh
    elif ari < 140.0: # Heavy Rain
        l0 = vl
        l1 = lo
        l2 = mo
        l3 = hi
        l4 = vh
    else: # Extreme Rain (>= 140 mm)
        l1 = vl
        l2 = lo
        l3 = mo
        l4 = hi + vh

    return {
        "l0": round(l0, 1),
        "l1": round(l1, 1),
        "l2": round(l2, 1),
        "l3": round(l3, 1),
        "l4": round(l4, 1),
        "l3_l4": round(l3 + l4, 1)
    }

def main():
    print("=" * 80)
    print("REAL-TIME METEOROLOGICAL TELEMETRY & NASA LHASA v2 NOWCAST")
    print("=" * 80)

    results = {}

    for key, cfg in MONITORED_STATES.items():
        daily = fetch_state_weather(cfg["lat"], cfg["lon"])
        times = daily.get("time", [])
        precip = daily.get("precipitation_sum", [])

        if not precip or len(precip) < 8:
            print(f"[WARN] Incomplete precipitation data for {cfg['name']}")
            continue

        # precip contains 7 past days + today (8 items)
        today_rain = precip[-1] if precip[-1] is not None else 0.0
        past_7_days_rain = precip[-8:-1] # past 7 days excluding today

        # Reverse so series = [R_today, R_yesterday, ..., R_6days_ago]
        series = [today_rain] + list(reversed(past_7_days_rain))
        
        # Calculate 7-day decaying weighted ARI
        ari = sum(series[t] * ARI_WEIGHTS[t] for t in range(min(len(series), len(ARI_WEIGHTS))))
        sum_7d = sum(past_7_days_rain) + today_rain

        susc = STATE_SUSC_DISTRIBUTION[key]
        nowcast = compute_lhasa_percentages(susc, ari)

        # Risk level determination
        if nowcast["l4"] > 5.0 or ari >= 140:
            status = "CRITICAL / SEVERE (Level 4)"
            status_color = "RED"
        elif nowcast["l3"] > 5.0 or ari >= 80:
            status = "WARNING (Level 3)"
            status_color = "ORANGE"
        elif nowcast["l2"] > 5.0 or ari >= 40:
            status = "WATCH (Level 2)"
            status_color = "YELLOW"
        elif nowcast["l1"] > 5.0:
            status = "ADVISORY (Level 1)"
            status_color = "LIGHT GREEN"
        else:
            status = "SAFE (Level 0)"
            status_color = "GREEN"

        results[key] = {
            "name": cfg["name"],
            "station": cfg["station"],
            "today_rain": round(today_rain, 1),
            "sum_7d": round(sum_7d, 1),
            "ari": round(ari, 1),
            "status": status,
            "status_color": status_color,
            "nowcast": nowcast,
            "corridor": cfg["corridor"],
            "timestamps": times[-8:]
        }

        print(f"\n[{cfg['name'].upper()}] - {cfg['station']}")
        print(f"  Live 24h Rain: {today_rain:.1f} mm | 7-Day Cumulative: {sum_7d:.1f} mm")
        print(f"  Decaying ARI : {ari:.1f} mm  --> Alert Status: {status}")
        print(f"  Hazard Breakdown: L0(Safe)={nowcast['l0']}% | L1={nowcast['l1']}% | L2={nowcast['l2']}% | L3(Warn)={nowcast['l3']}% | L4(Severe)={nowcast['l4']}%")
        print(f"  Critical Corridors: {cfg['corridor']}")

    # Save to JSON
    out_file = "data/processed/results/realtime_weather_lhasa.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[OK] Real-time nowcast report exported to {out_file}")

if __name__ == "__main__":
    main()

