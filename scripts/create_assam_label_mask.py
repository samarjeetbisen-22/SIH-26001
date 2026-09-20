"""
Assam Landslide Label Mask Creation
Buffers 105 historical landslide events with 150m radial buffer.
Rasterizes onto the 30m master grid.
Outputs:
- data/processed/labels/assam/assam_label_mask.tif
- data/processed/labels/assam/assam_event_buffers.gpkg
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

EVENTS_CSV = "data/raw/landslides/assam_events.csv"
REF_RASTER = "data/processed/factors/assam/assam_elevation.tif"
OUT_DIR    = "data/processed/labels/assam"
OUT_MASK   = os.path.join(OUT_DIR, "assam_label_mask.tif")
BUFFER_M   = 150

os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Assam Label Mask Creation")
print(f"Buffer radius: {BUFFER_M} m")
print("=" * 60)

events = pd.read_csv(EVENTS_CSV)
print(f"Loaded {len(events)} Assam events")

gdf = gpd.GeoDataFrame(
    events,
    geometry=gpd.points_from_xy(events['longitude'], events['latitude']),
    crs="EPSG:4326"
)

# Project to UTM 46N
gdf_utm = gdf.to_crs("EPSG:32646")
gdf_utm['geometry'] = gdf_utm.geometry.buffer(BUFFER_M)
print(f"Created {len(gdf_utm)} circular buffers (radius={BUFFER_M} m)")

with rasterio.open(REF_RASTER) as src:
    meta = src.meta.copy()
    transform = src.transform
    shape = (src.height, src.width)
    crs = src.crs

meta.update({'dtype': 'uint8', 'nodata': 255, 'count': 1})

shapes = [(geom, 1) for geom in gdf_utm.geometry if geom is not None]
mask = rasterize(
    shapes=shapes,
    out_shape=shape,
    transform=transform,
    fill=0,
    dtype='uint8',
    all_touched=False
)

n_positive = int(np.sum(mask == 1))
print(f"Positive pixels: {n_positive:,}")
print(f"Background pixels: {int(np.sum(mask == 0)):,}")

with rasterio.open(OUT_MASK, 'w', **meta) as dst:
    dst.write(mask, 1)
print(f"Saved label mask: {OUT_MASK}")

event_gpkg = os.path.join(OUT_DIR, "assam_event_buffers.gpkg")
gdf_utm.to_file(event_gpkg, driver="GPKG")
print(f"Saved event buffers: {event_gpkg}")
print("Label mask creation complete.")
