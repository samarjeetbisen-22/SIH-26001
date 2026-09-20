"""
Nagaland Training Dataset Builder
Samples all positive pixels from the label mask and equal negative pixels.
Adds lithology rasterized onto the master grid.
Output: data/processed/training/nagaland/nagaland_training.csv
"""

import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import warnings
warnings.filterwarnings('ignore')

# ---- CONFIG --------------------------------------------------------------
FACTORS_DIR = "data/processed/factors/nagaland"
LABEL_MASK  = "data/processed/labels/nagaland/nagaland_label_mask.tif"
LITH_GPKG   = "data/processed/lithology/nagaland/nagaland_lithology.gpkg"
OUT_DIR     = "data/processed/training/nagaland"
OUT_CSV     = os.path.join(OUT_DIR, "nagaland_training.csv")
RANDOM_SEED = 42

os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Nagaland Training Dataset Builder")
print("=" * 60)

# ---- Load label mask -----------------------------------------------------
print("\nLoading label mask ...")
with rasterio.open(LABEL_MASK) as src:
    labels = src.read(1).astype(np.float32)
    transform = src.transform
    shape = (src.height, src.width)
    crs = src.crs

n_positive = int(np.sum(labels == 1))
print(f"Positive pixels: {n_positive:,}")

# ---- Load terrain factors -----------------------------------------------
factor_files = {
    'elevation': os.path.join(FACTORS_DIR, "nagaland_elevation.tif"),
    'slope':     os.path.join(FACTORS_DIR, "nagaland_slope.tif"),
    'aspect':    os.path.join(FACTORS_DIR, "nagaland_aspect.tif"),
    'curvature': os.path.join(FACTORS_DIR, "nagaland_curvature.tif"),
    'twi':       os.path.join(FACTORS_DIR, "nagaland_twi.tif"),
}

print("\nLoading terrain factors ...")
factor_arrays = {}
for name, path in factor_files.items():
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
        nd = src.nodata if src.nodata is not None else -9999
        arr[arr == nd] = np.nan
        factor_arrays[name] = arr
        print(f"  {name:12s}: min={np.nanmin(arr):.2f}, max={np.nanmax(arr):.2f}, "
              f"valid={np.sum(np.isfinite(arr)):,}")

# ---- Rasterize lithology onto master grid --------------------------------
print("\nRasterizing lithology ...")
lith = gpd.read_file(LITH_GPKG)
print(f"  Loaded {len(lith)} lithology polygons")

# Use existing lith_id if available
if 'lith_id' not in lith.columns:
    glg_vals = lith['GLG'].dropna().unique()
    lith_id_map = {g: i+1 for i, g in enumerate(sorted(glg_vals))}
    lith['lith_id'] = lith['GLG'].map(lith_id_map).fillna(0).astype(int)
else:
    lith_id_map = {v: k for k, v in enumerate(lith['lith_id'].unique())}

# Reproject to match master grid CRS
if lith.crs != crs:
    lith = lith.to_crs(crs)

shapes = [(geom, int(lid)) for geom, lid in zip(lith.geometry, lith['lith_id'])
          if geom is not None and not geom.is_empty]
lith_arr = rasterize(
    shapes=shapes,
    out_shape=shape,
    transform=transform,
    fill=0,
    dtype='float32',
)
lith_arr = lith_arr.astype(np.float32)
lith_arr[lith_arr == 0] = np.nan  # NoData where no lithology
factor_arrays['lithology'] = lith_arr
print(f"  Lithology: unique IDs = {np.unique(lith_arr[np.isfinite(lith_arr)]).tolist()}")

# ---- Build valid pixel mask ---------------------------------------------
all_valid = np.ones(shape, dtype=bool)
for name, arr in factor_arrays.items():
    all_valid &= np.isfinite(arr)
all_valid &= (labels != 255)  # exclude nodata label

print(f"\nTotal valid pixels: {np.sum(all_valid):,}")

# ---- Sample positive pixels ---------------------------------------------
pos_rows, pos_cols = np.where((labels == 1) & all_valid)
n_pos = len(pos_rows)
print(f"Valid positive pixels: {n_pos:,}")

if n_pos == 0:
    print("ERROR: No valid positive pixels! Check alignment.")
    sys.exit(1)

# ---- Sample negative pixels ---------------------------------------------
neg_rows, neg_cols = np.where((labels == 0) & all_valid)
n_neg_avail = len(neg_rows)
print(f"Available negative pixels: {n_neg_avail:,}")

# Balanced sampling: match positive count
np.random.seed(RANDOM_SEED)
n_sample = n_pos
idx_neg = np.random.choice(n_neg_avail, size=n_sample, replace=False)
neg_rows_s = neg_rows[idx_neg]
neg_cols_s = neg_cols[idx_neg]

print(f"Sampled negatives: {n_sample:,} (1:1 balance)")

# ---- Build DataFrame ----------------------------------------------------
all_rows = np.concatenate([pos_rows, neg_rows_s])
all_cols = np.concatenate([pos_cols, neg_cols_s])
targets  = np.concatenate([np.ones(n_pos), np.zeros(n_sample)])

# Compute geographic coordinates
xs = transform.c + all_cols * transform.a + all_rows * transform.b
ys = transform.f + all_rows * transform.e + all_cols * transform.d

df = pd.DataFrame({'row': all_rows, 'col': all_cols, 'x': xs, 'y': ys})
for name, arr in factor_arrays.items():
    df[name] = arr[all_rows, all_cols]
df['target'] = targets.astype(int)

# Drop rows with any NaN in factors
df.dropna(subset=list(factor_arrays.keys()), inplace=True)
print(f"\nFinal training samples: {len(df):,}")
print(f"  Positive: {int(df['target'].sum()):,}")
print(f"  Negative: {int((df['target'] == 0).sum()):,}")

df.to_csv(OUT_CSV, index=False)
print(f"\nSaved: {OUT_CSV}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nFactor statistics:")
for col in ['elevation', 'slope', 'aspect', 'curvature', 'twi', 'lithology']:
    if col in df.columns:
        print(f"  {col:12s}: mean={df[col].mean():.3f}, std={df[col].std():.3f}")

print("\nDONE!")
