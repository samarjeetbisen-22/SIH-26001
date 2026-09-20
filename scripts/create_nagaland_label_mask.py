"""
Nagaland Label Mask Creation
Uses 150m circular buffer around 101 landslide event points.
Rasterizes buffers onto the 30m UTM master grid.
Output: data/processed/labels/nagaland/nagaland_label_mask.tif
"""

import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')

# ---- CONFIG --------------------------------------------------------------
EVENTS_CSV  = "data/raw/landslides/nagaland_events.csv"
REF_RASTER  = "data/processed/factors/nagaland/nagaland_elevation.tif"  # master grid
OUT_DIR     = "data/processed/labels/nagaland"
OUT_MASK    = os.path.join(OUT_DIR, "nagaland_label_mask.tif")
BUFFER_M    = 150   # radius in metres

os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Nagaland Label Mask Creation")
print(f"Buffer radius: {BUFFER_M} m")
print("=" * 60)

# ---- Load events ---------------------------------------------------------
events = pd.read_csv(EVENTS_CSV)
print(f"Loaded {len(events)} Nagaland events")
print(f"Lat range: {events['latitude'].min():.3f} - {events['latitude'].max():.3f}")
print(f"Lon range: {events['longitude'].min():.3f} - {events['longitude'].max():.3f}")

# Create GeoDataFrame in WGS84
gdf = gpd.GeoDataFrame(
    events,
    geometry=gpd.points_from_xy(events['longitude'], events['latitude']),
    crs="EPSG:4326"
)

# Project to UTM 46N
gdf_utm = gdf.to_crs("EPSG:32646")
print(f"Projected to EPSG:32646 (UTM Zone 46N)")
print(f"Event X range: {gdf_utm.geometry.x.min():.0f} - {gdf_utm.geometry.x.max():.0f} m")
print(f"Event Y range: {gdf_utm.geometry.y.min():.0f} - {gdf_utm.geometry.y.max():.0f} m")

# Create circular buffers
gdf_utm['geometry'] = gdf_utm.geometry.buffer(BUFFER_M)
print(f"Created {len(gdf_utm)} circular buffers (radius={BUFFER_M} m)")

# ---- Load reference raster metadata -------------------------------------
print(f"\nLoading master grid from: {REF_RASTER}")
with rasterio.open(REF_RASTER) as src:
    meta = src.meta.copy()
    transform = src.transform
    shape = (src.height, src.width)
    crs = src.crs
    print(f"   Shape: {shape[0]} x {shape[1]}")
    print(f"   CRS: {crs}")
    print(f"   Transform: {transform}")

meta.update({'dtype': 'uint8', 'nodata': 255, 'count': 1})

# ---- Rasterize buffers ---------------------------------------------------
print("\nRasterizing label buffers ...")
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
print(f"Positive pixels (landslide): {n_positive:,}")
print(f"Background pixels:           {int(np.sum(mask == 0)):,}")
print(f"Coverage: {n_positive / mask.size * 100:.2f}% of study area")

if n_positive == 0:
    print("ERROR: No positive pixels! Check coordinate alignment.")
    sys.exit(1)

# ---- Save mask -----------------------------------------------------------
with rasterio.open(OUT_MASK, 'w', **meta) as dst:
    dst.write(mask, 1)
print(f"\nSaved: {OUT_MASK}")

# ---- Also save the event GeoPackage for reference -----------------------
event_gpkg = os.path.join(OUT_DIR, "nagaland_event_buffers.gpkg")
gdf_utm.to_file(event_gpkg, driver="GPKG")
print(f"Saved event buffers: {event_gpkg}")

print("\nDONE - Label mask created successfully!")
print(f"  Positive pixels: {n_positive:,}")
print(f"  Buffer radius:   {BUFFER_M} m")
