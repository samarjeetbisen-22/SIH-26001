"""
Assam Full-Area Susceptibility Prediction
Loads trained XGBoost model, runs inference on every pixel, saves GeoTIFF + PNG.
Output: data/processed/results/assam/assam_susceptibility.tif/.png
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

# ---- CONFIG --------------------------------------------------------------
FACTORS_DIR = "data/processed/factors/assam"
LITH_GPKG   = "data/processed/lithology/assam/assam_lithology.gpkg"
MODEL_PATH  = "models/assam/assam_xgboost.pkl"
OUT_DIR     = "data/processed/results/assam"
FEATURES    = ['elevation', 'slope', 'aspect', 'curvature', 'twi', 'lithology']
BATCH_ROWS  = 200   # Process in row batches to save memory

os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Assam Full-Area Susceptibility Prediction")
print("=" * 60)

# ---- Load model ----------------------------------------------------------
model = joblib.load(MODEL_PATH)
print(f"Model loaded: {MODEL_PATH}")

# ---- Load terrain factors -----------------------------------------------
print("\nLoading factors ...")
factor_files = {
    'elevation': os.path.join(FACTORS_DIR, "assam_elevation.tif"),
    'slope':     os.path.join(FACTORS_DIR, "assam_slope.tif"),
    'aspect':    os.path.join(FACTORS_DIR, "assam_aspect.tif"),
    'curvature': os.path.join(FACTORS_DIR, "assam_curvature.tif"),
    'twi':       os.path.join(FACTORS_DIR, "assam_twi.tif"),
}

factor_arrays = {}
ref_meta = None
for name, path in factor_files.items():
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
        nd = src.nodata if src.nodata is not None else -9999
        arr[arr == nd] = np.nan
        factor_arrays[name] = arr
        if ref_meta is None:
            ref_meta = src.meta.copy()
            transform = src.transform
            crs = src.crs
            shape = (src.height, src.width)
    print(f"  {name:12s}: {arr.shape}")

ROWS, COLS = shape

# ---- Rasterize lithology ------------------------------------------------
print("\nRasterizing lithology ...")
lith = gpd.read_file(LITH_GPKG)
if lith.crs != crs:
    lith = lith.to_crs(crs)
if 'lith_id' not in lith.columns:
    glg_vals = lith['GLG'].dropna().unique()
    lith_id_map = {g: i+1 for i, g in enumerate(sorted(glg_vals))}
    lith['lith_id'] = lith['GLG'].map(lith_id_map).fillna(0).astype(int)
shapes = [(geom, int(lid)) for geom, lid in zip(lith.geometry, lith['lith_id'])
          if geom is not None]
lith_arr = rasterize(shapes=shapes, out_shape=shape,
                     transform=transform, fill=0, dtype='float32')
lith_arr[lith_arr == 0] = np.nan
factor_arrays['lithology'] = lith_arr
print(f"  Lithology unique IDs: {np.unique(lith_arr[np.isfinite(lith_arr)]).tolist()}")

# ---- Full-area inference in batches ------------------------------------
print(f"\nRunning inference ({ROWS} x {COLS} = {ROWS*COLS/1e6:.1f}M pixels) ...")
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

    if start_row % (BATCH_ROWS * 10) == 0:
        pct = start_row / ROWS * 100
        print(f"  {pct:.0f}% ...", flush=True)

n_inferred = int(np.sum(np.isfinite(susceptibility)))
print(f"\nInference complete: {n_inferred:,} valid pixels")
print(f"  Susceptibility range: {np.nanmin(susceptibility):.3f} - {np.nanmax(susceptibility):.3f}")
print(f"  Mean susceptibility: {np.nanmean(susceptibility):.3f}")

# ---- Save GeoTIFF -------------------------------------------------------
out_tif = os.path.join(OUT_DIR, "assam_susceptibility.tif")
meta = ref_meta.copy()
meta.update({'dtype': 'float32', 'nodata': -9999.0, 'count': 1, 'compress': 'lzw'})
susc_out = susceptibility.copy()
susc_out[~np.isfinite(susc_out)] = -9999.0
with rasterio.open(out_tif, 'w', **meta) as dst:
    dst.write(susc_out, 1)
print(f"\nGeoTIFF saved: {out_tif}")

# ---- Class distribution --------------------------------------------------
thresholds = [0, 0.2, 0.4, 0.6, 0.8, 1.001]
class_names = ['Very Low', 'Low', 'Moderate', 'High', 'Very High']
print("\nSusceptibility class distribution:")
for i, name in enumerate(class_names):
    mask = (susceptibility >= thresholds[i]) & (susceptibility < thresholds[i+1])
    cnt = int(np.sum(mask))
    pct = cnt / n_inferred * 100
    print(f"  {name:10s}: {cnt:>10,} px  ({pct:5.1f}%)")

# ---- Visualization -------------------------------------------------------
print("\nGenerating map ...")
fig, ax = plt.subplots(figsize=(12, 10))

cmap = mcolors.LinearSegmentedColormap.from_list(
    'susceptibility', ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027'], N=256
)
norm = mcolors.Normalize(vmin=0, vmax=1)

susc_display = susceptibility.copy()
susc_display[~np.isfinite(susc_display)] = np.nan

extent = [
    transform.c,
    transform.c + COLS * transform.a,
    transform.f + ROWS * transform.e,
    transform.f,
]
im = ax.imshow(susc_display, cmap=cmap, norm=norm, extent=extent, aspect='equal')
cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label("Landslide Susceptibility (0-1)", fontsize=11)

# Plot event locations
try:
    events_gdf = gpd.read_file("data/processed/labels/assam/assam_event_buffers.gpkg")
    event_pts = events_gdf.geometry.centroid
    ax.scatter(event_pts.x, event_pts.y, c='white', edgecolors='black', s=20, zorder=5,
               linewidths=0.8, alpha=0.9, label='Landslide events (n=105)')
    ax.legend(loc='lower right', fontsize=9)
except Exception:
    pass

ax.set_title("Assam Landslide Susceptibility Map\n"
             "XGBoost 6-Factor Model @ 30m | UTM Zone 46N (EPSG:32646)",
             fontsize=13, fontweight='bold')
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
ax.grid(True, alpha=0.2)

# Annotate Guwahati area (main event cluster)
ax.annotate("Guwahati /\nKamrup Cluster\n(48 events)",
            xy=(extent[0] + (extent[1]-extent[0])*0.3, extent[2] + (extent[3]-extent[2])*0.6),
            fontsize=8, color='navy', style='italic', ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

out_png = os.path.join(OUT_DIR, "assam_susceptibility_map.png")
plt.tight_layout()
plt.savefig(out_png, dpi=150, bbox_inches='tight')
plt.close()
print(f"Map saved: {out_png}")

print("\nDONE - Assam susceptibility prediction complete!")

