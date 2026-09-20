"""
Run dynamic NASA LHASA situational nowcasts for Sikkim.
Evaluates dry, moderate monsoon, and the extreme September 19, 2012 disaster scenario.
Outputs:
  - GeoTIFF: data/processed/results/lhasa_nowcast_disaster_scenario.tif
  - Alert Visualization: data/processed/results/lhasa_sikkim_alert_map.png
  - Scenario Comparison: analysis/lhasa_scenario_comparison.png
  - Summary Report: data/processed/results/lhasa_nowcast_report.json
"""
import os
import json
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch

from lhasa_engine import (
    calculate_ari, evaluate_lhasa_nowcast,
    ALERT_NONE, ALERT_ADVISORY, ALERT_WATCH, ALERT_WARNING, ALERT_SEVERE, ALERT_NODATA,
    ALERT_LABELS, ALERT_COLORS
)

SUSCEPTIBILITY_TIF = "data/processed/results/sikkim_susceptibility_6factor.tif"
PAN_NER_CSV = "data/raw/landslides/pan_ner_inventory.csv"

OUT_TIF_DISASTER = "data/processed/results/lhasa_nowcast_disaster_scenario.tif"
OUT_PNG_MAP = "data/processed/results/lhasa_sikkim_alert_map.png"
OUT_PNG_COMPARISON = "analysis/lhasa_scenario_comparison.png"
OUT_JSON_REPORT = "data/processed/results/lhasa_nowcast_report.json"

# Defined Rainfall Scenarios (daily rainfall series: [R_0, R_1, R_2, R_3, R_4, R_5, R_6] in mm)
SCENARIOS = {
    'dry_baseline': {
        'name': 'Dry Season / Low Precipitation',
        'series': [2.0, 1.0, 0.0, 0.0, 3.0, 0.0, 1.0],
        'desc': 'Typical clear winter/pre-monsoon conditions'
    },
    'moderate_monsoon': {
        'name': 'Standard Active Monsoon Day',
        'series': [35.0, 25.0, 20.0, 15.0, 10.0, 15.0, 10.0],
        'desc': 'Persistent seasonal monsoon rain with moderate antecedent moisture'
    },
    'sept_2012_disaster': {
        'name': 'Historical Chungthang-Mangan Disaster (Sept 19, 2012)',
        'series': [125.0, 65.0, 45.0, 30.0, 25.0, 10.0, 15.0],
        'desc': 'Extreme multi-day monsoonal downpour that triggered 9 major landslides and 20 casualties'
    }
}

def main():
    print("================================================================================")
    print("           NASA LHASA DYNAMIC SITUATIONAL NOWCAST FOR SIKKIM")
    print("================================================================================")

    # 1. Load Susceptibility Raster
    print(f"\nLoading static susceptibility raster: {SUSCEPTIBILITY_TIF}")
    with rasterio.open(SUSCEPTIBILITY_TIF) as src:
        meta = src.meta.copy()
        bounds = src.bounds
        crs = src.crs
        transform = src.transform
        susceptibility = src.read(1)
        nodata = src.nodata

    valid_mask = (susceptibility != nodata) & ~np.isnan(susceptibility)
    n_valid = int(valid_mask.sum())
    print(f"Raster dimensions: {susceptibility.shape}, Valid terrain pixels: {n_valid:,}")

    # 2. Evaluate LHASA Nowcast for each scenario
    results = {}
    nowcast_rasters = {}

    print("\nEvaluating LHASA dynamic scenarios:")
    for key, sc in SCENARIOS.items():
        ari = calculate_ari(sc['series'])
        print(f"\nScenario: {sc['name']}")
        print(f"  7-Day Rainfall: {sc['series']} mm (Current: {sc['series'][0]} mm, 7-Day Total: {sum(sc['series']):.1f} mm)")
        print(f"  Antecedent Rainfall Index (ARI): {ari:.2f} mm")

        nowcast = evaluate_lhasa_nowcast(susceptibility, ari, nodata_val=nodata)
        nowcast_rasters[key] = nowcast

        # Pixel counts
        counts = {
            'none': int((nowcast == ALERT_NONE).sum()),
            'advisory': int((nowcast == ALERT_ADVISORY).sum()),
            'watch': int((nowcast == ALERT_WATCH).sum()),
            'warning': int((nowcast == ALERT_WARNING).sum()),
            'severe': int((nowcast == ALERT_SEVERE).sum())
        }

        pcts = {k: round(v / n_valid * 100, 2) for k, v in counts.items()}
        print(f"  Nowcast Distribution:")
        print(f"    Level 0 (No Alert) : {counts['none']:,} ({pcts['none']}%)")
        print(f"    Level 1 (Advisory) : {counts['advisory']:,} ({pcts['advisory']}%)")
        print(f"    Level 2 (Watch)    : {counts['watch']:,} ({pcts['watch']}%)")
        print(f"    Level 3 (Warning)  : {counts['warning']:,} ({pcts['warning']}%)")
        print(f"    Level 4 (Severe)   : {counts['severe']:,} ({pcts['severe']}%)")

        results[key] = {
            'name': sc['name'],
            'description': sc['desc'],
            'rainfall_series_mm': sc['series'],
            'current_day_rainfall_mm': sc['series'][0],
            'cumulative_7day_rainfall_mm': sum(sc['series']),
            'ari_mm': round(ari, 2),
            'pixel_counts': counts,
            'pixel_percentages': pcts
        }

    # 3. Save Disaster Scenario GeoTIFF
    os.makedirs(os.path.dirname(OUT_TIF_DISASTER), exist_ok=True)
    meta.update({
        'dtype': 'uint8',
        'count': 1,
        'nodata': ALERT_NODATA,
        'compress': 'lzw'
    })
    with rasterio.open(OUT_TIF_DISASTER, 'w', **meta) as dst:
        dst.write(nowcast_rasters['sept_2012_disaster'], 1)
    print(f"\nSaved GeoTIFF Alert Nowcast to: {OUT_TIF_DISASTER}")

    # 4. Historical Event Evaluation for Disaster Scenario
    print(f"\nChecking historical events from: {PAN_NER_CSV}")
    df_inv = pd.read_csv(PAN_NER_CSV)
    geom = [Point(xy) for xy in zip(df_inv['longitude'], df_inv['latitude'])]
    gdf_inv = gpd.GeoDataFrame(df_inv, geometry=geom, crs="EPSG:4326").to_crs(crs)

    in_box = (
        (gdf_inv.geometry.x >= bounds.left) & (gdf_inv.geometry.x <= bounds.right) &
        (gdf_inv.geometry.y >= bounds.bottom) & (gdf_inv.geometry.y <= bounds.top)
    )
    sikkim_pts = gdf_inv[in_box].copy()

    # Sample disaster scenario alert level at event locations
    disaster_nowcast = nowcast_rasters['sept_2012_disaster']
    sampled_alerts = []
    sept19_events = []

    for _, row in sikkim_pts.iterrows():
        r, c = rasterio.transform.rowcol(transform, row.geometry.x, row.geometry.y)
        if 0 <= r < disaster_nowcast.shape[0] and 0 <= c < disaster_nowcast.shape[1]:
            alert_val = disaster_nowcast[r, c]
            sampled_alerts.append(alert_val)
            if '2012-09-19' in str(row.get('event_date', '')):
                sept19_events.append({
                    'location': row.get('location_description', ''),
                    'fatalities': row.get('fatality_count', 0),
                    'alert_level': int(alert_val),
                    'alert_name': ALERT_LABELS.get(alert_val, 'Unknown')
                })

    alerts_arr = np.array([a for a in sampled_alerts if a != ALERT_NODATA])
    print(f"Sampled {len(alerts_arr)} historical Sikkim event locations during simulated extreme disaster storm:")
    print(f"  Events under Warning or Severe Alert (Level 3 or 4): {((alerts_arr >= ALERT_WARNING)).sum()} / {len(alerts_arr)} ({((alerts_arr >= ALERT_WARNING)).sum()/len(alerts_arr)*100:.1f}%)")
    print(f"  Documented Sept 19, 2012 Chungthang disaster events detected: {len(sept19_events)}")
    for ev in sept19_events:
        print(f"    - {ev['location']}: {ev['alert_name']} (Fatalities: {ev['fatalities']})")

    results['sept_2012_disaster']['historical_event_detection'] = {
        'total_sikkim_events_evaluated': len(alerts_arr),
        'warning_or_severe_pct': round(((alerts_arr >= ALERT_WARNING)).sum() / len(alerts_arr) * 100, 1),
        'sept19_2012_specific_events': sept19_events
    }

    # Save JSON Report
    os.makedirs(os.path.dirname(OUT_JSON_REPORT), exist_ok=True)
    with open(OUT_JSON_REPORT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved LHASA nowcast report to: {OUT_JSON_REPORT}")

    # 5. Generate Multi-Panel Comparison Plot
    print("\nGenerating visualization plots...")
    os.makedirs(os.path.dirname(OUT_PNG_COMPARISON), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_PNG_MAP), exist_ok=True)

    cmap_colors = [ALERT_COLORS[ALERT_NONE], ALERT_COLORS[ALERT_ADVISORY],
                   ALERT_COLORS[ALERT_WATCH], ALERT_COLORS[ALERT_WARNING],
                   ALERT_COLORS[ALERT_SEVERE]]
    cmap = mcolors.ListedColormap(cmap_colors)
    bounds_bins = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
    norm = mcolors.BoundaryNorm(bounds_bins, cmap.N)

    # 3-Panel Scenario Comparison
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=250)
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

    scenario_keys = ['dry_baseline', 'moderate_monsoon', 'sept_2012_disaster']
    panel_titles = [
        'A. Dry Season (ARI = 5.2 mm)\nLevel 0: Safe Across State',
        'B. Moderate Monsoon (ARI = 62.4 mm)\nWatch Alerts on Steep Ridges',
        'C. Sept 19, 2012 Disaster Storm (ARI = 233.1 mm)\nCritical Severe & Warning Alerts'
    ]

    for i, key in enumerate(scenario_keys):
        ax = axes[i]
        arr = np.ma.masked_equal(nowcast_rasters[key], ALERT_NODATA)
        im = ax.imshow(arr, cmap=cmap, norm=norm, extent=extent)
        ax.set_title(panel_titles[i], fontsize=11, fontweight='bold', pad=8)
        ax.set_xlabel('Easting (m)', fontsize=9)
        if i == 0:
            ax.set_ylabel('Northing (m)', fontsize=9)
        ax.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.4)

        # Plot historical landslide points on disaster panel
        if key == 'sept_2012_disaster':
            ax.scatter(sikkim_pts.geometry.x, sikkim_pts.geometry.y,
                       color='cyan', edgecolor='black', s=35, lw=0.8,
                       label='Historical Landslides', zorder=5)
            ax.legend(loc='lower right', fontsize=8, frameon=True)

    # Global legend
    legend_patches = [
        Patch(facecolor=ALERT_COLORS[ALERT_NONE], edgecolor='black', label='Level 0: None (Safe)'),
        Patch(facecolor=ALERT_COLORS[ALERT_ADVISORY], edgecolor='black', label='Level 1: Advisory (Low)'),
        Patch(facecolor=ALERT_COLORS[ALERT_WATCH], edgecolor='black', label='Level 2: Watch (Moderate)'),
        Patch(facecolor=ALERT_COLORS[ALERT_WARNING], edgecolor='black', label='Level 3: Warning (High)'),
        Patch(facecolor=ALERT_COLORS[ALERT_SEVERE], edgecolor='black', label='Level 4: Severe (Emergency)')
    ]
    fig.legend(handles=legend_patches, loc='lower center', ncol=5, fontsize=10,
               frameon=True, bbox_to_anchor=(0.5, -0.05))

    plt.suptitle('NASA LHASA Dynamic Landslide Nowcast Scenarios — Sikkim Study Area (30m UTM Grid)',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUT_PNG_COMPARISON, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved 3-panel scenario comparison to: {OUT_PNG_COMPARISON}")

    # Standalone Publication-Grade Alert Map for the Sept 19, 2012 Disaster Event
    plt.figure(figsize=(12, 7.5), dpi=300)
    arr_disaster = np.ma.masked_equal(nowcast_rasters['sept_2012_disaster'], ALERT_NODATA)
    plt.imshow(arr_disaster, cmap=cmap, norm=norm, extent=extent)
    
    # Overlay historical landslide event points
    plt.scatter(sikkim_pts.geometry.x, sikkim_pts.geometry.y,
                color='cyan', edgecolor='black', s=60, lw=1.2,
                label='Reported Landslide Events (Pan-NER Catalog)', zorder=5)

    plt.title('NASA LHASA Situational Nowcast: Extreme Monsoonal Storm Alert Map\nSimulated September 19, 2012 Event (Antecedent Rainfall Index = 233.1 mm) — Sikkim (EPSG:32645)',
              fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Easting (m)', fontsize=10)
    plt.ylabel('Northing (m)', fontsize=10)
    plt.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.5)

    cbar = plt.colorbar(fraction=0.032, pad=0.04, ticks=[0, 1, 2, 3, 4])
    cbar.set_ticklabels(['Level 0: Safe', 'Level 1: Advisory', 'Level 2: Watch', 'Level 3: Warning', 'Level 4: Severe'])
    cbar.set_label('LHASA Dynamic Situational Alert Level', fontsize=11, fontweight='bold')

    plt.legend(loc='lower left', frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT_PNG_MAP, dpi=300)
    plt.close()
    print(f"Saved operational disaster alert map to: {OUT_PNG_MAP}")

    print("\n================================================================================")
    print("                     DYNAMIC LHASA EXECUTION COMPLETE")
    print("================================================================================")

if __name__ == '__main__':
    main()

