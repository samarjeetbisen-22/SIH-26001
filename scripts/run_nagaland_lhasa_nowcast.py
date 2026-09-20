"""
Nagaland LHASA Dynamic Nowcast
Runs 3 rainfall scenarios against the Nagaland susceptibility map.
Mirrors the Sikkim LHASA engine but for EPSG:32646 UTM Zone 46N.
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import rasterio
from rasterio.transform import from_bounds
import warnings
warnings.filterwarnings('ignore')

from lhasa_engine import calculate_ari, evaluate_lhasa_nowcast, ALERT_LABELS
# ---- CONFIG --------------------------------------------------------------
SUSC_TIF   = "data/processed/results/nagaland/nagaland_susceptibility.tif"
OUT_DIR    = "data/processed/results/nagaland"
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Nagaland LHASA Dynamic Nowcast")
print("=" * 60)

# ---- Load susceptibility map --------------------------------------------
print(f"\nLoading: {SUSC_TIF}")
with rasterio.open(SUSC_TIF) as src:
    susc = src.read(1).astype(np.float32)
    transform = src.transform
    crs = src.crs
    meta = src.meta.copy()
    nodata = src.nodata or -9999
    shape = susc.shape

susc[susc == nodata] = np.nan
valid_mask = np.isfinite(susc)
n_valid = int(np.sum(valid_mask))
print(f"  Shape: {shape}, Valid pixels: {n_valid:,}")
print(f"  Susceptibility: {np.nanmin(susc):.3f} - {np.nanmax(susc):.3f}")

# ---- Define Rainfall Scenarios ------------------------------------------
# Nagaland rainfall context: world's 2nd wettest monsoon region (after Meghalaya)
# NH-29 receives 2,000-3,500 mm/year; intense monsoon storms common

scenarios = {
    "Dry (Pre-Monsoon)": {
        "desc": "Clear days before monsoon season",
        "rainfall_7day": [0.0, 1.2, 0.5, 0.0, 2.1, 0.8, 0.3],
    },
    "Active Monsoon": {
        "desc": "Typical heavy monsoon (Jun-Sep)",
        "rainfall_7day": [18.5, 22.3, 35.1, 41.2, 28.7, 19.8, 12.4],
    },
    "Extreme Storm (NH-29 Cloudbursts)": {
        "desc": "Cloudburst event over Nagaland hills — NH-29 closure risk",
        "rainfall_7day": [5.2, 8.7, 45.3, 82.1, 118.4, 94.2, 61.8],
    },
}

print(f"\nRunning {len(scenarios)} rainfall scenarios ...")

results = {}
for scenario_name, cfg in scenarios.items():
    rain = cfg["rainfall_7day"]
    ari = calculate_ari(rain)
    alert_map = evaluate_lhasa_nowcast(susc, ari)
    alert_map_int = alert_map.astype(np.int16)
    alert_map_int[~valid_mask] = -1  # mark invalid as -1

    # Alert statistics
    stats = {}
    for level in range(5):
        cnt = int(np.sum(alert_map_int == level))
        pct = cnt / n_valid * 100

        stats[level] = {"count": cnt, "pct_of_valid": round(pct, 2)}
    
    results[scenario_name] = {
        "description": cfg["desc"],
        "rainfall_7day_mm": rain,
        "ari_mm": round(ari, 2),
        "alert_stats": stats,
    }
    print(f"\n  [{scenario_name}]")
    print(f"    ARI = {ari:.1f} mm")
    for level in range(5):
        print(f"    Level {level} ({ALERT_LABELS[level]:8s}): "
              f"{stats[level]['count']:>8,} px ({stats[level]['pct_of_valid']:5.1f}%)")

# ---- Save alert GeoTIFF for extreme scenario ----------------------------
# Re-run extreme scenario for saving
rain_extreme = scenarios["Extreme Storm (NH-29 Cloudbursts)"]["rainfall_7day"]
ari_extreme = calculate_ari(rain_extreme)
alert_extreme = evaluate_lhasa_nowcast(susc, ari_extreme).astype(np.int8)
alert_extreme[~valid_mask] = -1

meta_alert = meta.copy()
meta_alert.update({'dtype': 'int8', 'nodata': -1, 'count': 1})
tif_out = os.path.join(OUT_DIR, "nagaland_lhasa_alert_extreme.tif")
with rasterio.open(tif_out, 'w', **meta_alert) as dst:
    dst.write(alert_extreme, 1)
print(f"\nAlert GeoTIFF saved: {tif_out}")

# ---- Comparison Plot -----------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 7))
scenario_names = list(scenarios.keys())
alert_colors = ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027']
cmap_alert = mcolors.ListedColormap(alert_colors)
norm_alert = mcolors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5], cmap_alert.N)

for ax, name in zip(axes, scenario_names):
    cfg = scenarios[name]
    rain = cfg["rainfall_7day"]
    ari = calculate_ari(rain)
    alert = evaluate_lhasa_nowcast(susc, ari).astype(np.float32)
    alert[~valid_mask] = np.nan
    
    im = ax.imshow(alert, cmap=cmap_alert, norm=norm_alert, aspect='equal')
    ax.set_title(f"{name}\nARI = {ari:.1f} mm", fontsize=10, fontweight='bold')
    ax.set_xticks([]); ax.set_yticks([])

cbar = plt.colorbar(im, ax=axes.tolist(), fraction=0.02, pad=0.04,
                    ticks=[0, 1, 2, 3, 4])
cbar.set_ticklabels(["L0: Safe", "L1: Advisory", "L2: Watch", "L3: Warning", "L4: Severe"])
cbar.set_label("LHASA Alert Level", fontsize=11)

plt.suptitle("Nagaland LHASA Nowcast — 3 Rainfall Scenarios\n"
             "NH-29/NH-2 Landslide Early Warning System",
             fontsize=13, fontweight='bold', y=1.01)

plt.tight_layout()
compare_png = os.path.join(OUT_DIR, "nagaland_lhasa_scenario_comparison.png")
plt.savefig(compare_png, dpi=150, bbox_inches='tight')
plt.close()
print(f"Comparison map saved: {compare_png}")

# ---- Single map for extreme scenario -----------------------------------
fig, ax = plt.subplots(figsize=(11, 9))
disp = alert_extreme.astype(np.float32)
disp[alert_extreme == -1] = np.nan

im = ax.imshow(disp, cmap=cmap_alert, norm=norm_alert, aspect='equal')
cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04, ticks=[0, 1, 2, 3, 4])
cbar.set_ticklabels(["L0: Safe", "L1: Advisory", "L2: Watch", "L3: Warning", "L4: Severe"])
cbar.set_label("LHASA Alert Level", fontsize=11)

ax.set_title(f"Nagaland LHASA Alert Map — Extreme Storm Scenario\n"
             f"ARI = {ari_extreme:.1f} mm | NH-29/NH-2 Cloudburst Risk",
             fontsize=13, fontweight='bold')
ax.set_xticks([]); ax.set_yticks([])

ax.text(0.02, 0.02,
        f"Level 3+4 (Severe/Extreme): "
        f"{results['Extreme Storm (NH-29 Cloudbursts)']['alert_stats'][3]['pct_of_valid'] + results['Extreme Storm (NH-29 Cloudbursts)']['alert_stats'][4]['pct_of_valid']:.1f}% of area",
        transform=ax.transAxes, fontsize=10, color='white',
        bbox=dict(facecolor='black', alpha=0.6, boxstyle='round'))

alert_png = os.path.join(OUT_DIR, "nagaland_lhasa_alert_map.png")
plt.tight_layout()
plt.savefig(alert_png, dpi=150, bbox_inches='tight')
plt.close()
print(f"Alert map saved: {alert_png}")

# ---- Save JSON report ---------------------------------------------------
report = {
    "state": "Nagaland",
    "crs": "EPSG:32646",
    "susceptibility_model": "XGBoost 6-factor (AUC=93.63%)",
    "lhasa_version": "NASA LHASA v2 (ARI formula)",
    "scenarios": results,
}
json_out = os.path.join(OUT_DIR, "nagaland_lhasa_report.json")
with open(json_out, "w") as f:
    json.dump(report, f, indent=2)
print(f"Report saved: {json_out}")

print("\nDONE - Nagaland LHASA nowcast complete!")
ari_extreme_val = calculate_ari(scenarios["Extreme Storm (NH-29 Cloudbursts)"]["rainfall_7day"])
lvl4_pct = results["Extreme Storm (NH-29 Cloudbursts)"]["alert_stats"][4]["pct_of_valid"]
lvl3_pct = results["Extreme Storm (NH-29 Cloudbursts)"]["alert_stats"][3]["pct_of_valid"]
print(f"  Extreme storm: Level 4 = {lvl4_pct:.1f}%, Level 3 = {lvl3_pct:.1f}% of area")
