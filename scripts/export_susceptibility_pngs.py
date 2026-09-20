"""
Export Susceptibility TIFs as transparent PNG overlays for the web frontend.
- Downsamples to ~800px wide (manageable file size for static hosting)
- Applies the standard green-yellow-red susceptibility colormap
- Reprojects bounds to WGS84 for OpenLayers ImageStatic
- Outputs: sih2026final_v6/images/susceptibility/<state>_susc.png
           sih2026final_v6/images/susceptibility/overlay_bounds.json
"""

import os
import sys
import json
import numpy as np
import rasterio
from rasterio.warp import transform_bounds
import warnings
warnings.filterwarnings('ignore')

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    os.system("C:\\Python\\python.exe -m pip install Pillow -q")
    from PIL import Image

# ---- CONFIG ---------------------------------------------------------------
STATES = {
    "sikkim": {
        "tif": "data/processed/results/sikkim_susceptibility_6factor.tif",
        "label": "Sikkim",
        "events": 172,
        "auc": 93.80,
    },
    "nagaland": {
        "tif": "data/processed/results/nagaland/nagaland_susceptibility.tif",
        "label": "Nagaland",
        "events": 101,
        "auc": 93.63,
    },
    "meghalaya": {
        "tif": "data/processed/results/meghalaya/meghalaya_susceptibility.tif",
        "label": "Meghalaya",
        "events": 39,
        "auc": 95.07,
    },
    "assam": {
        "tif": "data/processed/results/assam/assam_susceptibility.tif",
        "label": "Assam",
        "events": 105,
        "auc": 95.18,
    },
}

OUT_DIR = "sih2026final_v6/images/susceptibility"
os.makedirs(OUT_DIR, exist_ok=True)

TARGET_WIDTH = 800   # Max output PNG width (height auto-calculated)

def apply_colormap(arr_norm, nodata_mask):
    """Apply graduated colormap with dynamic alpha tapering to keep base maps clear."""
    h, w = arr_norm.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    # Vivid gradient: Pale Green -> Lime -> Amber -> Orange -> Crimson -> Deep Red
    colors = np.array([
        [50, 160, 90],    # 0.00
        [160, 210, 80],   # 0.25
        [250, 200, 40],   # 0.45
        [245, 120, 25],   # 0.68
        [220, 30, 30],    # 0.88
        [160, 10, 10]     # 1.00
    ], dtype=np.float32)
    breakpoints = np.array([0.0, 0.25, 0.45, 0.68, 0.88, 1.0])

    r = np.interp(arr_norm, breakpoints, colors[:, 0])
    g = np.interp(arr_norm, breakpoints, colors[:, 1])
    b = np.interp(arr_norm, breakpoints, colors[:, 2])

    rgba[:, :, 0] = r.astype(np.uint8)
    rgba[:, :, 1] = g.astype(np.uint8)
    rgba[:, :, 2] = b.astype(np.uint8)

    # Dynamic Alpha Taper:
    # 0.00 - 0.10: 100% transparent (no green sheet over plains / valleys)
    # 0.10 - 0.30: Gentle ramp 0 to 120 (low risk slopes, subtle)
    # 0.30 - 0.60: Clear alert opacity 120 to 185 (moderate risk slopes)
    # 0.60 - 1.00: High alert opacity 185 to 225 (steep/vulnerable slopes pop out)
    alpha = np.zeros((h, w), dtype=np.float32)

    ramp_low = (arr_norm > 0.10) & (arr_norm <= 0.30)
    alpha[ramp_low] = np.interp(arr_norm[ramp_low], [0.10, 0.30], [0, 120])

    ramp_mid = (arr_norm > 0.30) & (arr_norm <= 0.60)
    alpha[ramp_mid] = np.interp(arr_norm[ramp_mid], [0.30, 0.60], [120, 185])

    ramp_high = arr_norm > 0.60
    alpha[ramp_high] = np.interp(arr_norm[ramp_high], [0.60, 1.0], [185, 225])

    alpha[nodata_mask] = 0.0
    rgba[:, :, 3] = alpha.astype(np.uint8)

    return rgba

# ---- Main loop -----------------------------------------------------------
overlay_bounds = {}

for state_key, cfg in STATES.items():
    tif_path = cfg["tif"]
    if not os.path.exists(tif_path):
        print(f"[SKIP] {state_key}: {tif_path} not found")
        continue

    print(f"\n[{cfg['label']}] Processing {tif_path} ...")

    with rasterio.open(tif_path) as src:
        # Get WGS84 bounds for OpenLayers
        bounds_utm = src.bounds
        src_crs = src.crs
        wgs84_bounds = transform_bounds(src_crs, "EPSG:4326",
                                        bounds_utm.left, bounds_utm.bottom,
                                        bounds_utm.right, bounds_utm.top)
        # [minLon, minLat, maxLon, maxLat]
        lon_min, lat_min, lon_max, lat_max = wgs84_bounds

        # Downsample to TARGET_WIDTH
        orig_h, orig_w = src.height, src.width
        scale = TARGET_WIDTH / orig_w
        new_w = TARGET_WIDTH
        new_h = int(orig_h * scale)

        print(f"   Original: {orig_h} x {orig_w} | Output: {new_h} x {new_w}")

        # Read at reduced resolution
        data = src.read(
            1,
            out_shape=(new_h, new_w),
            resampling=rasterio.enums.Resampling.average
        ).astype(np.float32)

        nodata_val = src.nodata if src.nodata is not None else -9999.0

    # Build masks
    nodata_mask = (data == nodata_val) | ~np.isfinite(data)
    valid = ~nodata_mask

    # Normalize 0-1
    arr_norm = np.clip(data, 0, 1)
    arr_norm[nodata_mask] = 0.0

    # Apply colormap
    rgba = apply_colormap(arr_norm, nodata_mask)

    # Save PNG
    out_png = os.path.join(OUT_DIR, f"{state_key}_susceptibility.png")
    img = Image.fromarray(rgba, mode="RGBA")
    img.save(out_png, "PNG", optimize=True)
    size_kb = os.path.getsize(out_png) / 1024
    print(f"   Saved: {out_png} ({size_kb:.0f} KB)")

    # Store bounds for JS
    overlay_bounds[state_key] = {
        "label": cfg["label"],
        "png": f"images/susceptibility/{state_key}_susceptibility.png",
        # OpenLayers extent format: [minX, minY, maxX, maxY] in EPSG:4326
        "extent_wgs84": [lon_min, lat_min, lon_max, lat_max],
        "events": cfg["events"],
        "test_auc_pct": cfg["auc"],
    }

    print(f"   WGS84 bounds: [{lon_min:.4f}, {lat_min:.4f}, {lon_max:.4f}, {lat_max:.4f}]")

# ---- Save bounds JSON ----------------------------------------------------
bounds_json_path = os.path.join(OUT_DIR, "overlay_bounds.json")
with open(bounds_json_path, "w") as f:
    json.dump(overlay_bounds, f, indent=2)
print(f"\nBounds JSON saved: {bounds_json_path}")

# ---- Also emit as JS constant for direct inclusion ----------------------
js_out = os.path.join("sih2026final_v6/images/susceptibility", "overlay_bounds.js")
with open(js_out, "w") as f:
    f.write("// Auto-generated by export_susceptibility_pngs.py\n")
    f.write("// Real susceptibility model overlay bounds for OpenLayers ImageStatic\n\n")
    f.write("const SUSC_OVERLAY_BOUNDS = ")
    json.dump(overlay_bounds, f, indent=2)
    f.write(";\n\nwindow.SUSC_OVERLAY_BOUNDS = SUSC_OVERLAY_BOUNDS;\n")
print(f"JS bounds file saved: {js_out}")

print("\n=== EXPORT COMPLETE ===")
for k, v in overlay_bounds.items():
    print(f"  {v['label']:10s}: {v['png']}")

