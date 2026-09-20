"""
Meghalaya Full-Area Landslide Susceptibility Prediction
Loads trained XGBoost model, runs inference across all pixels in the 30m master grid.
Outputs:
- data/processed/results/meghalaya/meghalaya_susceptibility.tif
- data/processed/results/meghalaya/meghalaya_susceptibility_map.png
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import joblib
import warnings
warnings.filterwarnings('ignore')

FACTORS_DIR = "data/processed/factors/meghalaya"
LITH_GPKG   = "data/processed/lithology/meghalaya/meghalaya_lithology.gpkg"
MODEL_PATH  = "models/meghalaya/meghalaya_xgboost.pkl"
OUT_DIR     = "data/processed/results/meghalaya"
FEATURES    = ['elevation', 'slope', 'aspect', 'curvature', 'twi', 'lithology']
BATCH_ROWS  = 200

os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Meghalaya Full-Area Susceptibility Prediction")
print("=" * 60)

model = joblib.load(MODEL_PATH)
print(f"Loaded model: {MODEL_PATH}")

factor_files = {
    'elevation': os.path.join(FACTORS_DIR, "meghalaya_elevation.tif"),
    'slope':     os.path.join(FACTORS_DIR, "meghalaya_slope.tif"),
    'aspect':    os.path.join(FACTORS_DIR, "meghalaya_aspect.tif"),
    'curvature': os.path.join(FACTORS_DIR, "meghalaya_curvature.tif"),
    'twi':       os.path.join(FACTORS_DIR, "meghalaya_twi.tif"),
}

print("\nLoading factor rasters ...")
factor_arrays = {}
ref_meta = None

for name, path in factor_files.items():
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
        nd = src.nodata if src.nodata is not None else -9999.0
        arr[arr == nd] = np.nan
        factor_arrays[name] = arr
        if ref_meta is None:
            ref_meta = src.meta.copy()
            transform = src.transform
            crs = src.crs
            shape = (src.height, src.width)
    print(f"  {name:12s}: shape={arr.shape}")

ROWS, COLS = shape

print("\nRasterizing lithology ...")
lith = gpd.read_file(LITH_GPKG)
if lith.crs != crs:
    lith = lith.to_crs(crs)

col = 'lith_group' if 'lith_group' in lith.columns else 'GLG'
glg_vals = sorted(lith[col].dropna().unique())
lith_id_map = {g: i + 1 for i, g in enumerate(glg_vals)}
lith['lith_id'] = lith[col].map(lith_id_map).fillna(0).astype(int)

shapes = [(geom, int(lid)) for geom, lid in zip(lith.geometry, lith['lith_id']) if geom is not None]
lith_arr = rasterize(shapes=shapes, out_shape=shape, transform=transform, fill=0, dtype='float32')
lith_arr[lith_arr == 0] = np.nan
factor_arrays['lithology'] = lith_arr

print(f"\nRunning batch inference across {ROWS} x {COLS} ({ROWS*COLS/1e6:.1f}M pixels) ...")
susceptibility = np.full((ROWS, COLS), np.nan, dtype=np.float32)

for start_row in range(0, ROWS, BATCH_ROWS):
    end_row = min(start_row + BATCH_ROWS, ROWS)
    batch_factors = []
    valid = np.ones((end_row - start_row, COLS), dtype=bool)
    for feat in FEATURES:
        chunk = factor_arrays[feat][start_row:end_row, :]
        valid &= np.isfinite(chunk)
        batch_factors.append(chunk)

    X_batch = np.stack(batch_factors, axis=-1).reshape(-1, len(FEATURES))
    valid_flat = valid.reshape(-1)
    probs = np.full(len(valid_flat), np.nan, dtype=np.float32)
    if valid_flat.any():
        probs[valid_flat] = model.predict_proba(X_batch[valid_flat])[:, 1].astype(np.float32)
    susceptibility[start_row:end_row, :] = probs.reshape(end_row - start_row, COLS)

    if start_row % (BATCH_ROWS * 5) == 0:
        pct = start_row / ROWS * 100
        print(f"  {pct:.1f}% processed ...", flush=True)

n_inferred = int(np.sum(np.isfinite(susceptibility)))
print(f"\nInference complete: {n_inferred:,} valid pixels")
print(f"  Susceptibility range: {np.nanmin(susceptibility):.3f} - {np.nanmax(susceptibility):.3f}")
print(f"  Mean susceptibility:  {np.nanmean(susceptibility):.3f}")

# Save GeoTIFF
out_tif = os.path.join(OUT_DIR, "meghalaya_susceptibility.tif")
meta = ref_meta.copy()
meta.update({'dtype': 'float32', 'nodata': -9999.0, 'count': 1})
susc_out = susceptibility.copy()
susc_out[~np.isfinite(susc_out)] = -9999.0
with rasterio.open(out_tif, 'w', **meta) as dst:
    dst.write(susc_out, 1)
print(f"GeoTIFF saved: {out_tif}")

# Susceptibility classification stats
thresholds = [0, 0.2, 0.4, 0.6, 0.8, 1.001]
class_names = ['Very Low', 'Low', 'Moderate', 'High', 'Very High']
print("\nSusceptibility Class Breakdown:")
for i, name in enumerate(class_names):
    mask = (susceptibility >= thresholds[i]) & (susceptibility < thresholds[i+1])
    cnt = int(np.sum(mask))
    pct = cnt / n_inferred * 100
    print(f"  {name:10s}: {cnt:>10,} px ({pct:5.1f}%)")

# Generate Map PNG
print("\nGenerating visualization map ...")
fig, ax = plt.subplots(figsize=(13, 7))

cmap = mcolors.LinearSegmentedColormap.from_list(
    'susceptibility', ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027'], N=256
)
norm = mcolors.Normalize(vmin=0, vmax=1)

susc_disp = susceptibility.copy()
susc_disp[~np.isfinite(susc_disp)] = np.nan

extent = [
    transform.c,
    transform.c + COLS * transform.a,
    transform.f + ROWS * transform.e,
    transform.f,
]

im = ax.imshow(susc_disp, cmap=cmap, norm=norm, extent=extent, aspect='equal')
cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.03)
cbar.set_label("Landslide Susceptibility Index (0–1)", fontsize=11)

events_gdf = gpd.read_file("data/processed/labels/meghalaya/meghalaya_event_buffers.gpkg")
event_pts = events_gdf.geometry.centroid
ax.scatter(event_pts.x, event_pts.y, c='white', edgecolors='black', s=25, zorder=5,
           linewidths=0.8, alpha=0.9, label=f'Historical Landslides (n={len(event_pts)})')

ax.set_title("Meghalaya Landslide Susceptibility Map (Shillong Plateau)\n"
             "XGBoost 6-Factor Model @ 30m | UTM Zone 46N (EPSG:32646)",
             fontsize=13, fontweight='bold')
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.2)

# Plateau and corridor annotations
mid_x = (extent[0] + extent[1]) / 2
mid_y = (extent[2] + extent[3]) / 2
ax.annotate("Cherrapunji / Mawsynram\nHigh-Risk Escarpment", xy=(mid_x + 50000, mid_y - 45000),
            fontsize=8, color='darkred', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffe6e6', alpha=0.85))
ax.annotate("NH-40 Guwahati-Shillong", xy=(mid_x + 80000, mid_y + 20000),
            fontsize=8, color='navy', style='italic',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='lightyellow', alpha=0.85))

out_png = os.path.join(OUT_DIR, "meghalaya_susceptibility_map.png")
plt.tight_layout()
plt.savefig(out_png, dpi=150, bbox_inches='tight')
plt.close()
print(f"Map saved: {out_png}")
print("Prediction and mapping complete.")

