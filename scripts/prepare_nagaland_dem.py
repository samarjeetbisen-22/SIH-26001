"""
Nagaland DEM Preprocessing Pipeline
Step 1: Reproject SRTM 30m DEM to UTM Zone 46N (EPSG:32646)
Step 2: Clip to Nagaland study area
Step 3: Compute terrain factors: Slope, Aspect, Curvature, TWI
Step 4: Save all factor rasters aligned to master grid

All rasters output to data/processed/factors/nagaland/
"""

import os
import sys
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.transform import from_bounds
from scipy.ndimage import uniform_filter
import warnings
warnings.filterwarnings('ignore')

# ---- CONFIGURATION -------------------------------------------------------
DEM_IN   = "data/raw/dem/nagaland/nagaland_dem_merged.tif"
OUT_DIR  = "data/processed/factors/nagaland"
UTM_DIR  = "data/processed/dem/nagaland/utm"
TARGET_CRS = "EPSG:32646"   # WGS84 / UTM Zone 46N for Nagaland
TARGET_RES = 30.0            # 30 m pixels

# Nagaland study bounds in WGS84 (with small buffer)
NAG_BOUNDS_WGS84 = (93.5, 25.1, 95.2, 27.0)  # (W, S, E, N)

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(UTM_DIR, exist_ok=True)

print("=" * 60)
print("Nagaland DEM Preprocessing")
print("=" * 60)

# ---- STEP 1: Reproject to UTM 46N at 30 m --------------------------------
utm_dem_path = os.path.join(UTM_DIR, "nagaland_dem_utm46n.tif")

if not os.path.exists(utm_dem_path):
    print(f"\n[1] Reprojecting DEM to {TARGET_CRS} at {TARGET_RES} m ...")
    with rasterio.open(DEM_IN) as src:
        transform, width, height = calculate_default_transform(
            src.crs, TARGET_CRS,
            src.width, src.height,
            left=NAG_BOUNDS_WGS84[0],
            bottom=NAG_BOUNDS_WGS84[1],
            right=NAG_BOUNDS_WGS84[2],
            top=NAG_BOUNDS_WGS84[3],
            resolution=TARGET_RES
        )
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': TARGET_CRS,
            'transform': transform,
            'width': width,
            'height': height,
            'nodata': -9999,
            'dtype': 'float32',
        })
        print(f"   Output shape: {height} x {width}")
        with rasterio.open(utm_dem_path, 'w', **kwargs) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=TARGET_CRS,
                resampling=Resampling.bilinear,
                src_nodata=-32768,
                dst_nodata=-9999,
            )
    print(f"   Saved: {utm_dem_path}")
else:
    print(f"\n[1] UTM DEM already exists: {utm_dem_path}")

# ---- Load UTM DEM --------------------------------------------------------
print("\n[2] Loading UTM DEM ...")
with rasterio.open(utm_dem_path) as src:
    dem = src.read(1).astype(np.float32)
    dem_transform = src.transform
    dem_meta = src.meta.copy()
    dem_nodata = src.nodata or -9999
    dem_crs = src.crs

ROWS, COLS = dem.shape
valid_mask = (dem != dem_nodata) & np.isfinite(dem)
dem[~valid_mask] = np.nan
print(f"   Shape: {ROWS} x {COLS}")
print(f"   Elevation: {np.nanmin(dem):.1f} – {np.nanmax(dem):.1f} m")
print(f"   Valid pixels: {np.sum(valid_mask):,}")

# Cell size in metres
cell_x = abs(dem_transform.a)
cell_y = abs(dem_transform.e)
print(f"   Cell size: {cell_x:.1f} m x {cell_y:.1f} m")

def save_raster(data, path, nodata=-9999.0, dtype='float32'):
    meta = dem_meta.copy()
    meta.update({'dtype': dtype, 'nodata': nodata, 'count': 1})
    out = data.astype(np.float32)
    out[~np.isfinite(out)] = nodata
    with rasterio.open(path, 'w', **meta) as dst:
        dst.write(out, 1)
    print(f"   Saved: {path}")

# ---- STEP 3: Elevation ---------------------------------------------------
elev_path = os.path.join(OUT_DIR, "nagaland_elevation.tif")
save_raster(dem, elev_path)
print("\n[3] Elevation saved.")

# ---- STEP 4: Slope -------------------------------------------------------
print("\n[4] Computing Slope ...")
# Sobel gradient method
from scipy.ndimage import sobel
dem_smooth = dem.copy()
dem_smooth[np.isnan(dem_smooth)] = 0

dz_dx = sobel(dem_smooth, axis=1) / (8.0 * cell_x)
dz_dy = sobel(dem_smooth, axis=0) / (8.0 * cell_y)

slope = np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))
slope[~valid_mask] = np.nan

slope_path = os.path.join(OUT_DIR, "nagaland_slope.tif")
save_raster(slope, slope_path)
print(f"   Slope range: {np.nanmin(slope):.1f} – {np.nanmax(slope):.1f} deg")

# ---- STEP 5: Aspect ------------------------------------------------------
print("\n[5] Computing Aspect ...")
aspect = np.degrees(np.arctan2(-dz_dy, dz_dx)) % 360
aspect[~valid_mask] = np.nan

aspect_path = os.path.join(OUT_DIR, "nagaland_aspect.tif")
save_raster(aspect, aspect_path)
print(f"   Aspect range: {np.nanmin(aspect):.1f} – {np.nanmax(aspect):.1f} deg")

# ---- STEP 6: Curvature ---------------------------------------------------
print("\n[6] Computing Curvature ...")
# Plan curvature using central differences
# Zxx + Zyy (Laplacian as proxy for curvature)
from scipy.ndimage import laplace, gaussian_filter

dem_filled = dem.copy()
dem_filled[np.isnan(dem_filled)] = np.nanmean(dem_filled)
dem_smooth2 = gaussian_filter(dem_filled, sigma=1)

Zxx = np.gradient(np.gradient(dem_smooth2, cell_x, axis=1), cell_x, axis=1)
Zyy = np.gradient(np.gradient(dem_smooth2, cell_y, axis=0), cell_y, axis=0)
curvature = Zxx + Zyy

curvature[~valid_mask] = np.nan
curv_path = os.path.join(OUT_DIR, "nagaland_curvature.tif")
save_raster(curvature, curv_path)
print(f"   Curvature range: {np.nanmin(curvature):.4f} – {np.nanmax(curvature):.4f}")

# ---- STEP 7: TWI (Topographic Wetness Index) -----------------------------
print("\n[7] Computing TWI ...")
# Approximate flow accumulation via local slope + contributing area proxy
# TWI = ln(As / tan(beta)) where As is specific catchment area
# Using simplified D8-like approach with upslope area estimation

slope_rad = np.radians(slope.copy())
slope_rad[slope_rad < 0.001] = 0.001  # avoid div/zero

# Approximate upslope area using uniform_filter as proxy for contributing area
# (simplified for non-WhiteboxTools environments)
cell_area = cell_x * cell_y
accum_proxy = uniform_filter(np.ones_like(dem) * cell_area, size=7)

# Specific catchment area
sca = accum_proxy / cell_x  # m

twi = np.log(sca / np.tan(slope_rad))
twi = np.clip(twi, -5, 25)
twi[~valid_mask] = np.nan

twi_path = os.path.join(OUT_DIR, "nagaland_twi.tif")
save_raster(twi, twi_path)
print(f"   TWI range: {np.nanmin(twi):.2f} – {np.nanmax(twi):.2f}")

# ---- SUMMARY -------------------------------------------------------------
print("\n" + "=" * 60)
print("TERRAIN FACTORS COMPLETE")
print("=" * 60)
factors = {
    'Elevation': elev_path,
    'Slope': slope_path,
    'Aspect': aspect_path,
    'Curvature': curv_path,
    'TWI': twi_path,
}
for name, path in factors.items():
    size = os.path.getsize(path) / 1e6
    print(f"  {name:12s}: {path} ({size:.1f} MB)")

print(f"\nAll factors: {ROWS} x {COLS} pixels at {cell_x:.0f} m, CRS={TARGET_CRS}")
print("DONE")
