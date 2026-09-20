"""
Assam LHASA Dynamic Nowcast
Runs 3 rainfall scenarios against the Assam susceptibility map.
Assam context: Brahmaputra valley floods, Dima Hasao cloudbursts, Barak Valley monsoons.
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
import warnings
warnings.filterwarnings('ignore')

from lhasa_engine import calculate_ari, evaluate_lhasa_nowcast, ALERT_LABELS

# ---- CONFIG --------------------------------------------------------------
SUSC_TIF   = "data/processed/results/assam/assam_susceptibility.tif"
OUT_DIR    = "data/processed/results/assam"
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Assam LHASA Dynamic Nowcast")
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
# Assam rainfall context:
#   - Brahmaputra valley receives 1,500-3,000 mm/year
#   - Dima Hasao (North Cachar Hills) gets extreme cloudburst events
#   - Barak Valley (Silchar) averages 3,500 mm/year
#   - Extreme monsoon events cause widespread slope failures

scenarios = {
    "Dry (Pre-Monsoon)": {
        "desc": "Clear days before monsoon onset (Mar-Apr)",
        "rainfall_7day": [0.0, 1.5, 0.5, 0.0, 2.0, 1.0, 0.2],
    },
    "Active Monsoon (Brahmaputra Valley)": {
        "desc": "Typical heavy monsoon over Assam plains (Jun-Sep)",
        "rainfall_7day": [20.0, 28.0, 42.0, 55.0, 35.0, 18.0, 10.0],
    },
    "Extreme Storm (Dima Hasao Cloudburst)": {
        "desc": "Extreme cloudburst over Dima Hasao hills - NH-27 / Barak Valley risk",
        "rainfall_7day": [8.0, 15.0, 55.0, 100.0, 130.0, 85.0, 50.0],
    },
}

print(f"\nRunning {len(scenarios)} rainfall scenarios ...")

results = {}
for scenario_name, cfg in scenarios.items():
    rain = cfg["rainfall_7day"]
    ari = calculate_ari(rain)
    alert_map = evaluate_lhasa_nowcast(susc, ari)
    alert_map_int = alert_map.astype(np.int16)
    alert_map_int[~valid_mask] = -1

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
rain_extreme = scenarios["Extreme Storm (Dima Hasao Cloudburst)"]["rainfall_7day"]
ari_extreme = calculate_ari(rain_extreme)
alert_extreme = evaluate_lhasa_nowcast(susc, ari_extreme).astype(np.int8)
alert_extreme[~valid_mask] = -1

meta_alert = meta.copy()
meta_alert.update({'dtype': 'int8', 'nodata': -1, 'count': 1})
tif_out = os.path.join(OUT_DIR, "assam_lhasa_alert_extreme.tif")
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
    short_name = name.split("(")[0].strip()
    ax.set_title(f"{short_name}\nARI = {ari:.1f} mm", fontsize=10, fontweight='bold')
    ax.set_xticks([]); ax.set_yticks([])

cbar = plt.colorbar(im, ax=axes.tolist(), fraction=0.02, pad=0.04,
                    ticks=[0, 1, 2, 3, 4])
cbar.set_ticklabels(["L0: Safe", "L1: Advisory", "L2: Watch", "L3: Warning", "L4: Severe"])
cbar.set_label("LHASA Alert Level", fontsize=11)

plt.suptitle("Assam LHASA Nowcast -- 3 Rainfall Scenarios\n"
             "Brahmaputra Valley / Dima Hasao Landslide Early Warning",
             fontsize=13, fontweight='bold', y=1.01)

plt.tight_layout()
compare_png = os.path.join(OUT_DIR, "assam_lhasa_scenario_comparison.png")
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

ax.set_title(f"Assam LHASA Alert Map -- Extreme Storm Scenario\n"
             f"ARI = {ari_extreme:.1f} mm | Dima Hasao Cloudburst Risk",
             fontsize=13, fontweight='bold')
ax.set_xticks([]); ax.set_yticks([])

lvl4 = results["Extreme Storm (Dima Hasao Cloudburst)"]["alert_stats"][4]["pct_of_valid"]
lvl3 = results["Extreme Storm (Dima Hasao Cloudburst)"]["alert_stats"][3]["pct_of_valid"]
ax.text(0.02, 0.02,
        f"Level 3+4 (Warning/Severe): {lvl3 + lvl4:.1f}% of area",
        transform=ax.transAxes, fontsize=10, color='white',
        bbox=dict(facecolor='black', alpha=0.6, boxstyle='round'))

alert_png = os.path.join(OUT_DIR, "assam_lhasa_alert_map.png")
plt.tight_layout()
plt.savefig(alert_png, dpi=150, bbox_inches='tight')
plt.close()
print(f"Alert map saved: {alert_png}")

# ---- Save JSON report ---------------------------------------------------
report = {
    "state": "Assam",
    "crs": "EPSG:32646",
    "susceptibility_model": "XGBoost 6-factor",
    "lhasa_version": "NASA LHASA v2 (ARI formula)",
    "scenarios": results,
}
json_out = os.path.join(OUT_DIR, "assam_lhasa_report.json")
with open(json_out, "w") as f:
    json.dump(report, f, indent=2)
print(f"Report saved: {json_out}")

print("\nDONE - Assam LHASA nowcast complete!")
print(f"  Extreme storm ARI: {ari_extreme:.1f} mm")
print(f"  Level 4 Severe: {lvl4:.1f}%, Level 3 Warning: {lvl3:.1f}%")

