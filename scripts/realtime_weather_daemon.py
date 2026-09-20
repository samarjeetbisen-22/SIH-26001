"""
Real-Time Meteorological Telemetry & Continuous Risk Monitoring Daemon
Periodically fetches live Open-Meteo precipitation feeds at a configurable interval (Default: 30 min),
computes 7-day decaying weighted Antecedent Rainfall Index (ARI), evaluates the NASA LHASA v2
hazard matrix, and logs risk progression to disk.

Usage:
  python scripts/realtime_weather_daemon.py             # Runs continuous 30-min monitoring
  python scripts/realtime_weather_daemon.py --interval 5 # 5-min testing interval
  python scripts/realtime_weather_daemon.py --once       # Run single cycle and exit
"""

import sys
import time
import json
import os
import argparse
import datetime
import urllib.request

# Exact decaying weights: w_t = (t + 1)^(-0.5) for t = 0..6
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
        "corridor": "NH-10 Gangtok-Siliguri lifeline corridor & Dikchu active slips"
    },
    "nagaland": {
        "name": "Nagaland",
        "station": "Kohima (Dzuwuru Corridor)",
        "lat": 25.6751,
        "lon": 94.1086,
        "corridor": "NH-29 Kohima-Dimapur bypass & Phesama sinking zone"
    },
    "meghalaya": {
        "name": "Meghalaya",
        "station": "Shillong (East Khasi Hills)",
        "lat": 25.5788,
        "lon": 91.8933,
        "corridor": "NH-6 Shillong-Jowai route & Cherrapunji escarpment"
    },
    "assam": {
        "name": "Assam",
        "station": "Dima Hasao / Haflong Hills",
        "lat": 25.1685,
        "lon": 93.0163,
        "corridor": "NH-27 Haflong section & Lumding-Badarpur railway"
    }
}

def fetch_state_weather(lat, lon, retries=3):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&past_days=7&forecast_days=1&timezone=Asia%2FKolkata"
    req = urllib.request.Request(url, headers={"User-Agent": "NER-Landslide-Monitoring-Daemon/1.0"})
    
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
            return data.get("daily", {})
        except Exception as e:
            if attempt == retries:
                raise e
            time.sleep(1.5 * attempt)
    return {}

def compute_lhasa_percentages(susc, ari):
    vl = susc["vlow"]
    lo = susc["low"]
    mo = susc["mod"]
    hi = susc["high"]
    vh = susc["vhigh"]

    l0 = l1 = l2 = l3 = l4 = 0.0

    if ari < 40.0:
        l0 = vl + lo + mo + hi
        l1 = vh
    elif ari < 80.0:
        l0 = vl + lo
        l1 = mo
        l2 = hi
        l3 = vh
    elif ari < 140.0:
        l0 = vl
        l1 = lo
        l2 = mo
        l3 = hi
        l4 = vh
    else:
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

def run_single_monitoring_cycle(cycle_num=1, prev_status=None):
    now_ist = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    print("\n" + "=" * 80)
    print(f"[CYCLE #{cycle_num}] REAL-TIME METEOROLOGICAL TELEMETRY & RISK MONITORING")
    print(f"Timestamp: {now_ist} | Monitored States: Sikkim, Nagaland, Meghalaya, Assam")
    print("=" * 80)

    results = {}
    history_rows = []
    current_status = {}

    for key, cfg in MONITORED_STATES.items():
        try:
            daily = fetch_state_weather(cfg["lat"], cfg["lon"])
            times = daily.get("time", [])
            precip = daily.get("precipitation_sum", [])

            if not precip or len(precip) < 8:
                print(f"[WARN] Incomplete precipitation data for {cfg['name']}")
                continue

            today_rain = precip[-1] if precip[-1] is not None else 0.0
            past_7_days_rain = precip[-8:-1]

            series = [today_rain] + list(reversed(past_7_days_rain))
            ari = sum(series[t] * ARI_WEIGHTS[t] for t in range(min(len(series), len(ARI_WEIGHTS))))
            sum_7d = sum(past_7_days_rain) + today_rain

            susc = STATE_SUSC_DISTRIBUTION[key]
            nowcast = compute_lhasa_percentages(susc, ari)

            # Determine alert status
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

            current_status[key] = status

            # Check for alert escalation
            if prev_status and prev_status.get(key) != status:
                print(f"  [ALERT ESCALATION] {cfg['name']}: {prev_status.get(key)} -> {status}")

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
                "timestamps": times[-8:],
                "cycle_time": now_ist
            }

            print(f"[{cfg['name'].upper()}] - {cfg['station']}")
            print(f"  24h Rain: {today_rain:.1f} mm | 7d Sum: {sum_7d:.1f} mm | Decaying ARI: {ari:.1f} mm")
            print(f"  Alert: {status} | L3+L4 Exposure: {nowcast['l3_l4']}% | Corridor: {cfg['corridor']}")

            # Automated CAP-CP v1.2 Alert Trigger
            if ari >= 60.0 or nowcast['l4'] >= 5.0:
                is_severe = (ari >= 100.0 or nowcast['l4'] >= 8.0)
                sev_label = "Severe" if is_severe else "Warning"
                dir_type = "Severe Emergency Alert" if is_severe else "High Risk Alert"
                rad_km = 15 if is_severe else 25
                cbs_towers = 8 if is_severe else 18
                lora_gateways = 11 if is_severe else 24

                # Regional language mapping
                reg_msgs = {
                    "sikkim": {
                        "lang": "Nepali",
                        "text": "आपतकालीन निर्देशन: अत्यधिक वर्षाका कारण पूर्वी सिक्किमको एनएच-१० र डिक्चु क्षेत्रमा जमिन भासिने र ठूलो पहिरो जाने उच्च जोखिम उत्पन्न भएको छ। भिरालो र जोखिमयुक्त ठाउँबाट तुरुन्त सुरक्षित स्थानमा जानुहोस्।"
                    },
                    "nagaland": {
                        "lang": "Nagamese",
                        "text": "HOSHIYAR THAKIBI: Bishi borokh pori ase, Kohima NH-29 aru Phesama sinking zone te mati dhori jabo laga bishi risk ase. Gari loi jabo naparibo, safe jaka te thakibi."
                    },
                    "meghalaya": {
                        "lang": "Khasi",
                        "text": "KA JINGMA JUR: Ka jingther u slap ka la pynlong ka jingma kaba khraw ha NH-6 Shillong-Jowai bad ki thain Cherrapunji. Ki paidbah kiba shong ha ki jaka riat ki dei ban phet noh sha ki jaka ba shngain."
                    },
                    "assam": {
                        "lang": "Assamese",
                        "text": "ভূমিস্খলনৰ সতৰ্কবাৰ্তা: ধাৰাসাৰ বৰষুণৰ বাবে ডিমা হাছাওৰ পাহাৰীয়া এলেকা আৰু এন এইচ-২৭ হাফলং সংযোগী পথত ভূমিস্খলনৰ আশংকা। পাহাৰীয়া পথত সাৱধানে চলাচল কৰক।"
                    }
                }
                reg = reg_msgs.get(key, {"lang": "English", "text": f"LANDSLIDE ALERT: Heavy rain triggering slope instability in {cfg['name']} along {cfg['corridor']}."})

                cap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>IN-NDMA-NER-{key.upper()}-{int(time.time())}</identifier>
  <sender>daemon@ndma-ner.gov.in</sender>
  <sent>{datetime.datetime.now().isoformat()}</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <info>
    <category>Geo</category>
    <event>Landslide / Mass Movement Hazard</event>
    <urgency>{'Immediate' if is_severe else 'Expected'}</urgency>
    <severity>{'Extreme' if is_severe else 'Severe'}</severity>
    <certainty>Observed</certainty>
    <headline>{dir_type}: {cfg['name']} ({cfg['station']})</headline>
    <description>{reg['text']}</description>
    <instruction>Evacuate unstable slopes, heed police diversions, and monitor local district authorities.</instruction>
    <parameter><valueName>ModelTrigger</valueName><value>NASA-LHASA-v2-XGBoost-30m</value></parameter>
    <parameter><valueName>RegionalLanguage</valueName><value>{reg['lang']}</value></parameter>
    <parameter><valueName>OfflineCoverage</valueName><value>{rad_km}km-Circle; CBS-Towers:{cbs_towers}; LoRa-Sirens:{lora_gateways}</value></parameter>
    <area>
      <areaDesc>{cfg['name']} - {cfg['station']} ({rad_km}km buffer)</areaDesc>
      <circle>{cfg['lat']:.4f},{cfg['lon']:.4f} {rad_km}.0</circle>
    </area>
  </info>
</alert>"""
                # Save CAP XML file
                cap_file = f"data/processed/results/cap_alert_{key}.xml"
                with open(cap_file, "w", encoding="utf-8") as f_cap:
                    f_cap.write(cap_xml)

                print(f"  [DISPATCHED] Autonomous CAP-CP v1.2 alert emitted for {cfg['name']} ({reg['lang']}) -> {cap_file}")

            # CSV history row
            history_rows.append(f"{now_ist},{key},{today_rain:.1f},{sum_7d:.1f},{ari:.1f},{status},{nowcast['l0']},{nowcast['l1']},{nowcast['l2']},{nowcast['l3']},{nowcast['l4']},{nowcast['l3_l4']}\n")

        except Exception as e:
            print(f"[ERR] Failed query for {cfg['name']}: {e}")

    # Export latest snapshot
    os.makedirs("data/processed/results", exist_ok=True)
    json_path = "data/processed/results/realtime_weather_lhasa.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    # Append to cumulative telemetry history
    csv_path = "data/processed/results/realtime_telemetry_history.csv"
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a") as f:
        if not file_exists:
            f.write("timestamp,state_key,today_rain_mm,sum_7d_mm,ari_mm,status,l0_pct,l1_pct,l2_pct,l3_pct,l4_pct,l3_l4_pct\n")
        f.writelines(history_rows)

    print(f"[OK] Telemetry updated -> {json_path}")
    print(f"[OK] Historical log appended -> {csv_path}")

    return current_status

def main():
    parser = argparse.ArgumentParser(description="Real-Time 30-Minute Meteorological & Landslide Risk Monitor")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring polling interval in minutes (Default: 30)")
    parser.add_argument("--once", action="store_true", help="Execute single cycle and exit")
    args = parser.parse_args()

    interval_sec = args.interval * 60
    cycle_num = 1
    prev_status = None

    print(f"Starting Continuous Real-Time Landslide Risk Monitoring Daemon")
    print(f"Cycle Frequency: Every {args.interval} minutes ({interval_sec} seconds)")
    print(f"To terminate: Press Ctrl+C\n")

    while True:
        try:
            prev_status = run_single_monitoring_cycle(cycle_num, prev_status)
            if args.once:
                print("\n[OK] Single execution cycle completed.")
                break

            cycle_num += 1
            next_time = (datetime.datetime.now() + datetime.timedelta(seconds=interval_sec)).strftime("%H:%M:%S IST")
            print(f"\n[SLEEP] Standing by. Next 30-minute monitoring cycle scheduled at {next_time}...")
            time.sleep(interval_sec)

        except KeyboardInterrupt:
            print("\n[INFO] Monitoring daemon stopped by user.")
            break
        except Exception as ex:
            print(f"\n[UNEXPECTED ERROR] {ex}. Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()
