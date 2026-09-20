"""
Meghalaya Dynamic NASA LHASA Situational Nowcast
Couples static 30m susceptibility with 7-day decaying Antecedent Rainfall Index (ARI).
Runs 3 scenarios:
1. Dry Pre-Monsoon
2. Active Monsoon (Cherrapunji/Mawsynram Normal)
3. Catastrophic Cloudburst / Extreme Escarpment Storm
Outputs:
- data/processed/results/meghalaya/meghalaya_lhasa_alert_extreme.tif
- data/processed/results/meghalaya/meghalaya_lhasa_scenario_comparison.png
- data/processed/results/meghalaya/meghalaya_lhasa_alert_map.png
- data/processed/results/meghalaya/meghalaya_lhasa_report.json
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

sys.path.insert(0, "scripts")
from lhasa_engine import calculate_ari, evaluate_lhasa_nowcast, ALERT_LABELS

SUSC_TIF = "data/processed/results/meghalaya/meghalaya_susceptibility.tif"
OUT_DIR  = "data/processed/results/meghalaya"
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Meghalaya NASA LHASA Dynamic Nowcast")
print("=" * 60)

with rasterio.open(SUSC_TIF) as src:
    susc = src.read(1).astype(np.float32)
    transform = src.transform
    crs = src.crs
    meta = src.meta.copy()
    nodata = src.nodata or -9999.0
    shape = susc.shape

susc[susc == nodata] = np.nan
valid_mask = np.isfinite(susc)
n_valid = int(np.sum(valid_mask))
print(f"Loaded susceptibility raster: {shape}, valid pixels={n_valid:,}")

# Scenarios tailored to Meghalaya's world-record rainfall belt
scenarios = {
    "Dry (Winter / Pre-Monsoon)": {
        "desc": "Winter dry spells / clear skies over Shillong Plateau",
        "rainfall_7day": [0.0, 0.8, 0.2, 0.0, 1.5, 0.4, 0.0],
    },
    "Active Monsoon (Cherrapunji Surge)": {
        "desc": "Heavy seasonal monsoon rains across southern plateau escarpment",
        "rainfall_7day": [25.0, 32.0, 48.0, 55.0, 38.0, 22.0, 15.0],
    },
    "Catastrophic Cloudburst / Escarpment Storm": {
        "desc": "Extreme orographic cloudburst along Mawsynram/Cherrapunji cliffs (NH-44 risk)",
        "rainfall_7day": [12.0, 28.0, 85.0, 140.0, 175.0, 110.0, 65.0],
    }
}

results = {}
alert_colors = ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027']
cmap_alert = mcolors.ListedColormap(alert_colors)
norm_alert = mcolors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5], cmap_alert.N)

for name, cfg in scenarios.items():
    rain = cfg["rainfall_7day"]
    ari = calculate_ari(rain)
    alert = evaluate_lhasa_nowcast(susc, ari)
    alert_int = alert.astype(np.int16)
    alert_int[~valid_mask] = -1

    stats = {}
    for lvl in range(5):
        cnt = int(np.sum(alert_int == lvl))
        pct = cnt / n_valid * 100
        stats[lvl] = {"count": cnt, "pct_of_valid": round(pct, 2)}

    results[name] = {
        "description": cfg["desc"],
        "rainfall_7day_mm": rain,
        "ari_mm": round(ari, 2),
        "alert_stats": stats,
    }

    print(f"\n[{name}] ARI = {ari:.1f} mm")
    for lvl in range(5):
        print(f"  Level {lvl} ({ALERT_LABELS[lvl]:8s}): {stats[lvl]['count']:>10,} px ({stats[lvl]['pct_of_valid']:5.1f}%)")

# Save GeoTIFF for extreme scenario
rain_ext = scenarios["Catastrophic Cloudburst / Escarpment Storm"]["rainfall_7day"]
ari_ext = calculate_ari(rain_ext)
alert_ext = evaluate_lhasa_nowcast(susc, ari_ext).astype(np.int8)
alert_ext[~valid_mask] = -1

meta_alert = meta.copy()
meta_alert.update({'dtype': 'int8', 'nodata': -1, 'count': 1})
tif_out = os.path.join(OUT_DIR, "meghalaya_lhasa_alert_extreme.tif")
with rasterio.open(tif_out, 'w', **meta_alert) as dst:
    dst.write(alert_ext, 1)
print(f"\nAlert GeoTIFF saved: {tif_out}")

# Comparison 3-panel plot
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for ax, name in zip(axes, scenarios.keys()):
    rain = scenarios[name]["rainfall_7day"]
    ari = calculate_ari(rain)
    alert = evaluate_lhasa_nowcast(susc, ari).astype(np.float32)
    alert[~valid_mask] = np.nan

    im = ax.imshow(alert, cmap=cmap_alert, norm=norm_alert, aspect='equal')
    ax.set_title(f"{name}\nARI = {ari:.1f} mm", fontsize=10, fontweight='bold')
    ax.set_xticks([]); ax.set_yticks([])

cbar = plt.colorbar(im, ax=axes.tolist(), fraction=0.02, pad=0.04, ticks=[0, 1, 2, 3, 4])
cbar.set_ticklabels(["L0: Safe", "L1: Advisory", "L2: Watch", "L3: Warning", "L4: Severe"])
cbar.set_label("LHASA Alert Level", fontsize=11)

plt.suptitle("Meghalaya Dynamic LHASA Nowcast — 3 Multi-Scenario Projections\n"
             "Shillong Plateau & Cherrapunji / Mawsynram Escarpments",
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
cmp_png = os.path.join(OUT_DIR, "meghalaya_lhasa_scenario_comparison.png")
plt.savefig(cmp_png, dpi=150, bbox_inches='tight')
plt.close()
print(f"Scenario comparison map saved: {cmp_png}")

# Operational alert map for extreme storm
fig, ax = plt.subplots(figsize=(12, 7))
disp = alert_ext.astype(np.float32)
disp[alert_ext == -1] = np.nan

im = ax.imshow(disp, cmap=cmap_alert, norm=norm_alert, aspect='equal')
cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.03, ticks=[0, 1, 2, 3, 4])
cbar.set_ticklabels(["L0: Safe", "L1: Advisory", "L2: Watch", "L3: Warning", "L4: Severe"])
cbar.set_label("LHASA Alert Level", fontsize=11)

ax.set_title(f"Meghalaya LHASA Alert Map — Catastrophic Storm Scenario\n"
             f"Antecedent Rainfall Index (ARI) = {ari_ext:.1f} mm | Plateau Escarpment Cloudburst",
             fontsize=13, fontweight='bold')
ax.set_xticks([]); ax.set_yticks([])

lvl3_pct = results["Catastrophic Cloudburst / Escarpment Storm"]["alert_stats"][3]["pct_of_valid"]
lvl4_pct = results["Catastrophic Cloudburst / Escarpment Storm"]["alert_stats"][4]["pct_of_valid"]
ax.text(0.02, 0.04,
        f"Level 3+4 (Warning + Severe Emergency): {lvl3_pct + lvl4_pct:.1f}% of study area\n"
        f"Level 4 (Severe Critical): {lvl4_pct:.1f}%",
        transform=ax.transAxes, fontsize=10, color='white',
        bbox=dict(facecolor='black', alpha=0.65, boxstyle='round,pad=0.4'))

alert_png = os.path.join(OUT_DIR, "meghalaya_lhasa_alert_map.png")
plt.tight_layout()
plt.savefig(alert_png, dpi=150, bbox_inches='tight')
plt.close()
print(f"Operational alert map saved: {alert_png}")

report = {
    "state": "Meghalaya",
    "crs": "EPSG:32646",
    "susceptibility_model": "XGBoost 6-factor (AUC=95.07%)",
    "lhasa_version": "NASA LHASA v2 (ARI decaying formula)",
    "scenarios": results,
}
json_out = os.path.join(OUT_DIR, "meghalaya_lhasa_report.json")
with open(json_out, "w") as f:
    json.dump(report, f, indent=2)
print(f"Report saved: {json_out}")
print("Meghalaya LHASA nowcast execution complete.")

