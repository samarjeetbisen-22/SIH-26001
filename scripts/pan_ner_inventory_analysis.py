"""
Pan-NER Landslide Inventory Analysis and Regional Spatial Mapping.
Analyzes 507 historical events across all 8 North-Eastern states:
Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura.
Outputs:
  - data/processed/results/pan_ner_inventory_map.png
  - data/processed/results/pan_ner_regional_summary.json
"""
import os
import json
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.cm as cm

CSV_PATH = "data/raw/landslides/pan_ner_inventory.csv"
OUT_PNG = "data/processed/results/pan_ner_inventory_map.png"
OUT_JSON = "data/processed/results/pan_ner_regional_summary.json"

NER_STATES = ['Assam', 'Nagaland', 'Manipur', 'Arunachal Pradesh', 'Sikkim', 'Mizoram', 'Meghalaya', 'Tripura']

STATE_COLORS = {
    'Assam': '#1f77b4',
    'Nagaland': '#ff7f0e',
    'Manipur': '#2ca02c',
    'Arunachal Pradesh': '#d62728',
    'Sikkim': '#9467bd',
    'Mizoram': '#8c564b',
    'Meghalaya': '#e377c2',
    'Tripura': '#17becf',
    'Other': '#7f7f7f'
}

def resolve_state(row):
    st = str(row['admin_division_name']).strip()
    if st in NER_STATES:
        return st
    desc = str(row['location_description']).lower()
    for s in NER_STATES:
        if s.lower() in desc:
            return s
    return 'Other'

def main():
    print("================================================================================")
    print("           PAN-NER REGIONAL LANDSLIDE INVENTORY ANALYSIS")
    print("================================================================================")
    
    df = pd.read_csv(CSV_PATH)
    print(f"Total historical records: {len(df)}")

    # 1. State Assignment Resolution
    df['state'] = df.apply(resolve_state, axis=1)
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    df['year'] = df['event_date'].dt.year
    df['month'] = df['event_date'].dt.month

    # 2. State-by-State Breakdown
    state_counts = df['state'].value_counts().to_dict()
    print("\nState-by-State Event Counts:")
    for s, c in sorted(state_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {s:<20}: {c:>3} events ({c/len(df)*100:.1f}%)")

    # 3. Trigger Mechanisms
    trigger_counts = df['landslide_trigger'].fillna('unknown').value_counts().to_dict()
    print("\nPrimary Trigger Mechanisms:")
    for t, c in sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:6]:
        print(f"  {t:<20}: {c:>3} events ({c/len(df)*100:.1f}%)")

    # 4. Casualty Statistics
    total_fatalities = int(df['fatality_count'].fillna(0).sum())
    total_injuries = int(df['injury_count'].fillna(0).sum())
    deadly_events = int((df['fatality_count'] > 0).sum())
    print(f"\nCasualty Statistics:")
    print(f"  Total recorded fatalities : {total_fatalities}")
    print(f"  Total recorded injuries   : {total_injuries}")
    print(f"  Events with casualties    : {deadly_events} ({deadly_events/len(df)*100:.1f}%)")

    # Top lethal events
    top_lethal = df[df['fatality_count'] > 0].sort_values('fatality_count', ascending=False).head(5)
    print("\nTop Severe Disaster Events:")
    for _, r in top_lethal.iterrows():
        print(f"  {str(r['event_date'])[:10]} | {r['state']:<18} | {int(r['fatality_count'])} deaths | {str(r['location_description'])[:45]}")

    # 5. Key Highway Corridor Extraction
    highways = ['nh 39', 'nh 29', 'nh 37', 'nh 53', 'nh 10', 'nh 31a', 'nh 44', 'nh 54', 'nh 13', 'nh 2']
    corridor_hits = {}
    for h in highways:
        corridor_hits[h.upper()] = int(df['location_description'].str.contains(h, case=False, na=False).sum())
    print("\nKey Lifeline Transport Corridor Landslide Counts:")
    for h, c in sorted(corridor_hits.items(), key=lambda x: x[1], reverse=True):
        if c > 0:
            print(f"  {h:<10}: {c} recorded landslide blockages")

    # 6. Save JSON Summary Report
    summary_data = {
        'total_regional_events': len(df),
        'temporal_coverage': f"{int(df['year'].min())} - {int(df['year'].max())}",
        'bounding_box': {
            'min_lat': float(df.latitude.min()),
            'max_lat': float(df.latitude.max()),
            'min_lon': float(df.longitude.min()),
            'max_lon': float(df.longitude.max())
        },
        'state_distribution': state_counts,
        'trigger_distribution': trigger_counts,
        'casualty_summary': {
            'total_fatalities': total_fatalities,
            'total_injuries': total_injuries,
            'events_with_fatalities': deadly_events
        },
        'corridor_landslide_counts': corridor_hits
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w') as f:
        json.dump(summary_data, f, indent=2)
    print(f"\nSaved regional inventory summary to: {OUT_JSON}")

    # 7. Render Pan-NER Spatial Map
    print(f"Rendering Pan-NER regional map to: {OUT_PNG}")
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)

    plt.figure(figsize=(15, 9), dpi=300)
    ax = plt.subplot(1, 1, 1)

    # Plot events by state
    for s in NER_STATES:
        sub = df[df['state'] == s]
        if len(sub) == 0:
            continue
        color = STATE_COLORS.get(s, '#7f7f7f')

        # Marker size based on fatalities (minimum 35, scaled up for fatal events)
        sizes = 35 + sub['fatality_count'].fillna(0) * 15

        ax.scatter(
            sub['longitude'], sub['latitude'],
            c=color, s=sizes, alpha=0.8, edgecolors='black', linewidth=0.7,
            label=f"{s} (n={len(sub)})", zorder=4
        )

    # Annotate state cluster centroids
    state_centroids = {
        'Sikkim': (88.5, 27.5),
        'Assam (Guwahati)': (91.8, 26.2),
        'Assam (Barail)': (93.1, 25.1),
        'Meghalaya': (91.4, 25.5),
        'Nagaland': (94.3, 26.1),
        'Manipur': (93.9, 24.8),
        'Mizoram': (92.8, 23.7),
        'Arunachal Pradesh': (94.0, 27.8),
        'Tripura': (91.7, 23.9)
    }
    for name, (cx, cy) in state_centroids.items():
        ax.text(cx, cy + 0.15, name, fontsize=8.5, fontweight='bold',
                color='#1a1a1a', ha='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='gray', lw=0.5))

    ax.set_title('Pan-NER Landslide Inventory Distribution — All 8 North-Eastern Region States (n=507 Events)\n'
                 'Bubble Size Scales with Recorded Disaster Casualties (2007–2021)',
                 fontsize=13, fontweight='bold', pad=14)
    ax.set_xlabel('Longitude (°E)', fontsize=11)
    ax.set_ylabel('Latitude (°N)', fontsize=11)
    ax.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.6)
    ax.set_xlim([87.8, 97.3])
    ax.set_ylim([22.0, 29.7])

    # Legends
    leg1 = ax.legend(loc='upper left', frameon=True, fontsize=9, title="NER States", title_fontsize=10)
    ax.add_artist(leg1)

    # Secondary casualty size legend
    cas_handles = [
        plt.scatter([], [], s=35, c='gray', edgecolors='black', alpha=0.7, label='0 deaths / damage'),
        plt.scatter([], [], s=35 + 5 * 15, c='gray', edgecolors='black', alpha=0.7, label='5 deaths'),
        plt.scatter([], [], s=35 + 20 * 15, c='gray', edgecolors='black', alpha=0.7, label='20 deaths')
    ]
    ax.legend(handles=cas_handles, loc='lower right', frameon=True, fontsize=8.5, title="Severity", title_fontsize=9.5)

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=300)
    plt.close()
    print(f"Saved regional inventory map to: {OUT_PNG}")

if __name__ == '__main__':
    main()

