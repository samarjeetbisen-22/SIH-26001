"""
Meghalaya Training Dataset Builder
Samples positive pixels from label mask and equal negative pixels from background.
Rasterizes regional lithology onto master grid.
Output: data/processed/training/meghalaya/meghalaya_training.csv
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

FACTORS_DIR = "data/processed/factors/meghalaya"
LABEL_MASK  = "data/processed/labels/meghalaya/meghalaya_label_mask.tif"
LITH_GPKG   = "data/processed/lithology/meghalaya/meghalaya_lithology.gpkg"
OUT_DIR     = "data/processed/training/meghalaya"
OUT_CSV     = os.path.join(OUT_DIR, "meghalaya_training.csv")
RANDOM_SEED = 42

os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Meghalaya Training Dataset Builder")
print("=" * 60)

with rasterio.open(LABEL_MASK) as src:
    labels = src.read(1).astype(np.float32)
    transform = src.transform
    shape = (src.height, src.width)
    crs = src.crs

factor_files = {
    'elevation': os.path.join(FACTORS_DIR, "meghalaya_elevation.tif"),
    'slope':     os.path.join(FACTORS_DIR, "meghalaya_slope.tif"),
    'aspect':    os.path.join(FACTORS_DIR, "meghalaya_aspect.tif"),
    'curvature': os.path.join(FACTORS_DIR, "meghalaya_curvature.tif"),
    'twi':       os.path.join(FACTORS_DIR, "meghalaya_twi.tif"),
}

print("\nLoading terrain factors ...")
factor_arrays = {}
for name, path in factor_files.items():
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
        nd = src.nodata if src.nodata is not None else -9999.0
        arr[arr == nd] = np.nan
        factor_arrays[name] = arr
        print(f"  {name:12s}: valid={np.sum(np.isfinite(arr)):,}")

print("\nRasterizing lithology ...")
lith = gpd.read_file(LITH_GPKG)
if lith.crs != crs:
    lith = lith.to_crs(crs)

col = 'lith_group' if 'lith_group' in lith.columns else 'GLG'
glg_vals = sorted(lith[col].dropna().unique())
lith_id_map = {g: i + 1 for i, g in enumerate(glg_vals)}
lith['lith_id'] = lith[col].map(lith_id_map).fillna(0).astype(int)

shapes = [(geom, int(lid)) for geom, lid in zip(lith.geometry, lith['lith_id'])
          if geom is not None and not geom.is_empty]
lith_arr = rasterize(
    shapes=shapes,
    out_shape=shape,
    transform=transform,
    fill=0,
    dtype='float32'
)
lith_arr[lith_arr == 0] = np.nan
factor_arrays['lithology'] = lith_arr

all_valid = np.ones(shape, dtype=bool)
for name, arr in factor_arrays.items():
    all_valid &= np.isfinite(arr)
all_valid &= (labels != 255)

print(f"\nTotal valid pixels across all 6 factors: {np.sum(all_valid):,}")

pos_rows, pos_cols = np.where((labels == 1) & all_valid)
n_pos = len(pos_rows)
print(f"Valid positive pixels: {n_pos:,}")

neg_rows, neg_cols = np.where((labels == 0) & all_valid)
n_neg_avail = len(neg_rows)
print(f"Available negative pixels: {n_neg_avail:,}")

np.random.seed(RANDOM_SEED)
idx_neg = np.random.choice(n_neg_avail, size=n_pos, replace=False)
neg_rows_s = neg_rows[idx_neg]
neg_cols_s = neg_cols[idx_neg]

all_rows = np.concatenate([pos_rows, neg_rows_s])
all_cols = np.concatenate([pos_cols, neg_cols_s])
targets  = np.concatenate([np.ones(n_pos), np.zeros(n_pos)])

xs = transform.c + all_cols * transform.a + all_rows * transform.b
ys = transform.f + all_rows * transform.e + all_cols * transform.d

df = pd.DataFrame({'row': all_rows, 'col': all_cols, 'x': xs, 'y': ys})
for name, arr in factor_arrays.items():
    df[name] = arr[all_rows, all_cols]
df['target'] = targets.astype(int)

df.dropna(subset=list(factor_arrays.keys()), inplace=True)
print(f"\nFinal balanced training samples: {len(df):,}")
print(f"  Positive: {int(df['target'].sum()):,}")
print(f"  Negative: {int((df['target'] == 0).sum()):,}")

df.to_csv(OUT_CSV, index=False)
print(f"Saved: {OUT_CSV}")
print("Training dataset construction complete.")

