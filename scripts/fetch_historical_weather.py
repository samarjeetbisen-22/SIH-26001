import json
import urllib.request
import datetime
import time

with open('sih2026final_v6/js/historical-events.js', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('[')
end = text.rfind(']') + 1
events = json.loads(text[start:end])
print(f"Total events in file: {len(events)}")

# Fetch real weather for events across NER
weather_db = {}

# Process in batches of 10 events to avoid rate limit
for i in range(0, min(60, len(events)), 10):
    batch = events[i:i+10]
    # For each event, determine start_date (date - 3 days) and end_date (date)
    for ev in batch:
        ev_id = str(ev['id'])
        dt_str = ev['date']
        try:
            dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d')
            dt_start = dt - datetime.timedelta(days=3)
            start_str = dt_start.strftime('%Y-%m-%d')
            end_str = dt.strftime('%Y-%m-%d')
            
            url = f"https://archive-api.open-meteo.com/v1/archive?latitude={ev['lat']:.4f}&longitude={ev['lon']:.4f}&start_date={start_str}&end_date={end_str}&daily=precipitation_sum,rain_sum&timezone=Asia%2FKolkata"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
                daily = data.get('daily', {})
                precip = daily.get('precipitation_sum', [0, 0, 0, 0])
                time_list = daily.get('time', [])
                
                # Replace None with 0.0
                precip = [0.0 if p is None else round(float(p), 1) for p in precip]
                
                # Pad to 4 days if needed
                while len(precip) < 4:
                    precip.insert(0, 0.0)
                if len(precip) > 4:
                    precip = precip[-4:]
                    
                weather_db[ev_id] = {
                    'dates': time_list if len(time_list) == 4 else [start_str, (dt-datetime.timedelta(days=2)).strftime('%Y-%m-%d'), (dt-datetime.timedelta(days=1)).strftime('%Y-%m-%d'), end_str],
                    'precipitation': precip,
                    'is_real_era5': True
                }
                print(f"  Event {ev_id} ({ev['location']}) {end_str}: {precip}")
        except Exception as e:
            print(f"  Error on event {ev_id}: {e}")
        time.sleep(0.15) # Polite delay

with open('sih2026final_v6/js/historical-weather-cache.json', 'w', encoding='utf-8') as f:
    json.dump(weather_db, f, indent=2)

print(f"Successfully cached {len(weather_db)} real ERA5 event weather series!")
