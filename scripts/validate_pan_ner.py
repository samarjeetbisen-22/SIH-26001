"""
Validate Sikkim 6-Factor Landslide Susceptibility Map against independent
historical landslide events from the user-provided pan-NER inventory.
Outputs:
  - data/processed/results/pan_ner_validation_report.json
  - analysis/pan_ner_sikkim_overlay.png
"""
import os
import json
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import rasterio
import matplotlib.pyplot as plt

PAN_NER_CSV = "data/raw/landslides/pan_ner_inventory.csv"
SUSCEPTIBILITY_TIF = "data/processed/results/sikkim_susceptibility_6factor.tif"
REPORT_JSON = "data/processed/results/pan_ner_validation_report.json"
PLOT_OUTPUT = "analysis/pan_ner_sikkim_overlay.png"

def main():
    print("--- STEP 6: EXTERNAL VALIDATION AGAINST PAN-NER HISTORICAL EVENTS ---")
    
    # 1. Load CSV
    df = pd.read_csv(PAN_NER_CSV)
    print(f"Total events in pan-NER inventory: {len(df)}")

    # 2. Open Susceptibility Raster
    with rasterio.open(SUSCEPTIBILITY_TIF) as src:
        bounds = src.bounds
        crs = src.crs
        transform = src.transform
        raster_data = src.read(1)
        nodata = src.nodata

    print(f"Master Raster Bounds (UTM): {bounds}")

    # 3. Create GeoDataFrame and reproject to raster CRS
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    gdf_utm = gdf.to_crs(crs)

    # 4. Filter events that fall within raster spatial bounding box
    in_extent = (
        (gdf_utm.geometry.x >= bounds.left) &
        (gdf_utm.geometry.x <= bounds.right) &
        (gdf_utm.geometry.y >= bounds.bottom) &
        (gdf_utm.geometry.y <= bounds.top)
    )
    sikkim_events = gdf_utm[in_extent].copy()
    print(f"Events intersecting Sikkim raster extent: {len(sikkim_events)}")

    # 5. Sample predicted susceptibility value at each event location
    sampled_probs = []
    valid_events = []

    for idx, row in sikkim_events.iterrows():
        x, y = row.geometry.x, row.geometry.y
        r, c = rasterio.transform.rowcol(transform, x, y)
        if 0 <= r < raster_data.shape[0] and 0 <= c < raster_data.shape[1]:
            val = raster_data[r, c]
            if val != nodata and not np.isnan(val):
                sampled_probs.append(float(val))
                valid_events.append(row)

    sikkim_events_valid = gpd.GeoDataFrame(valid_events, crs=crs)
    sikkim_events_valid['predicted_prob'] = sampled_probs

    print(f"Events with valid predicted susceptibility: {len(sikkim_events_valid)}")

    probs = np.array(sampled_probs)
    mean_prob = float(np.mean(probs))
    median_prob = float(np.median(probs))
    min_prob = float(np.min(probs))
    max_prob = float(np.max(probs))

    # Calculate hit rates in risk classes
    n_vhigh = int((probs >= 0.8).sum())
    n_high = int(((probs >= 0.6) & (probs < 0.8)).sum())
    n_mod = int(((probs >= 0.4) & (probs < 0.6)).sum())
    n_low = int(((probs >= 0.2) & (probs < 0.4)).sum())
    n_vlow = int((probs < 0.2).sum())

    total = len(probs)
    pct_high_plus = (n_high + n_vhigh) / total * 100
    pct_mod_plus = (n_mod + n_high + n_vhigh) / total * 100

    print("\nValidation Performance on Independent Historical Events:")
    print(f"  Mean Predicted Susceptibility:   {mean_prob:.3f} (vs. study-area background mean of 0.201)")
    print(f"  Median Predicted Susceptibility: {median_prob:.3f}")
    print(f"  Range:                          [{min_prob:.3f}, {max_prob:.3f}]")
    print(f"  Events in High or Very High:    {n_high + n_vhigh}/{total} ({pct_high_plus:.1f}%)")
    print(f"  Events in Moderate or above:    {n_mod + n_high + n_vhigh}/{total} ({pct_mod_plus:.1f}%)")

    # 6. Save JSON Report
    report = {
        'total_pan_ner_records': len(df),
        'sikkim_events_in_extent': len(sikkim_events),
        'sikkim_events_valid': total,
        'mean_susceptibility_at_events': mean_prob,
        'median_susceptibility_at_events': median_prob,
        'background_mean_susceptibility': 0.2013,
        'zonation_hit_counts': {
            'very_high_gt_0.8': n_vhigh,
            'high_0.6_to_0.8': n_high,
            'moderate_0.4_to_0.6': n_mod,
            'low_0.2_to_0.4': n_low,
            'very_low_lt_0.2': n_vlow
        },
        'hit_rates': {
            'high_or_very_high_pct': pct_high_plus,
            'moderate_or_above_pct': pct_mod_plus
        },
        'sample_evaluated_events': [
            {
                'date': str(r.get('event_date', '')),
                'location': str(r.get('location_description', '')),
                'trigger': str(r.get('landslide_trigger', '')),
                'predicted_prob': round(r['predicted_prob'], 3)
            }
            for _, r in sikkim_events_valid.head(10).iterrows()
        ]
    }

    os.makedirs(os.path.dirname(REPORT_JSON), exist_ok=True)
    with open(REPORT_JSON, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved validation report to: {REPORT_JSON}")

    # 7. Generate Overlay Plot
    os.makedirs(os.path.dirname(PLOT_OUTPUT), exist_ok=True)
    plt.figure(figsize=(12, 7), dpi=250)

    plot_data = np.ma.masked_equal(raster_data, nodata)
    cmap = plt.get_cmap('RdYlGn_r').copy()
    cmap.set_bad(color='#e0e0e0')

    im = plt.imshow(plot_data, cmap=cmap, vmin=0.0, vmax=1.0, extent=[
        bounds.left, bounds.right, bounds.bottom, bounds.top
    ])
    cbar = plt.colorbar(im, fraction=0.032, pad=0.04)
    cbar.set_label('Predicted Susceptibility P(Failure)', fontsize=11, fontweight='bold')

    # Scatter historical events
    xs = sikkim_events_valid.geometry.x
    ys = sikkim_events_valid.geometry.y
    plt.scatter(xs, ys, color='blue', edgecolor='white', s=50, lw=1.2,
                label=f'Pan-NER Historical Events (n={len(xs)})', zorder=5)

    plt.title('Independent Validation: Historical Landslide Events Overlay\nSikkim 6-Factor Landslide Susceptibility Map',
              fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Easting (m)', fontsize=10)
    plt.ylabel('Northing (m)', fontsize=10)
    plt.legend(loc='upper right', frameon=True)
    plt.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.5)

    plt.tight_layout()
    plt.savefig(PLOT_OUTPUT, dpi=300)
    plt.close()
    print(f"Saved validation overlay plot to: {PLOT_OUTPUT}")

if __name__ == '__main__':
    main()
