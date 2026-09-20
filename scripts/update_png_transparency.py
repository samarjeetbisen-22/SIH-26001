import os
import rasterio
import numpy as np
from PIL import Image

STATES = {
    'sikkim': {
        'tif': 'data/processed/results/sikkim_susceptibility_6factor.tif',
        'label': 'Sikkim',
    },
    'nagaland': {
        'tif': 'data/processed/results/nagaland/nagaland_susceptibility.tif',
        'label': 'Nagaland',
    },
    'meghalaya': {
        'tif': 'data/processed/results/meghalaya/meghalaya_susceptibility.tif',
        'label': 'Meghalaya',
    },
    'assam': {
        'tif': 'data/processed/results/assam/assam_susceptibility.tif',
        'label': 'Assam',
    },
}

OUT_DIR = 'sih2026final_v6/images/susceptibility'
TARGET_WIDTH = 800

def apply_colormap_alpha_taper(arr_norm, nodata_mask):
    h, w = arr_norm.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    # Color breakpoints:
    # 0.0 -> subtle pale green [50, 160, 90]
    # 0.25 -> chartreuse/lime [160, 210, 80]
    # 0.45 -> bright golden amber [250, 200, 40]
    # 0.68 -> vivid orange [245, 120, 25]
    # 0.88 -> bold crimson red [220, 30, 30]
    # 1.00 -> dark red [160, 10, 10]
    colors = np.array([
        [50, 160, 90],
        [160, 210, 80],
        [250, 200, 40],
        [245, 120, 25],
        [220, 30, 30],
        [160, 10, 10]
    ], dtype=np.float32)
    breakpoints = np.array([0.0, 0.25, 0.45, 0.68, 0.88, 1.0])

    r = np.interp(arr_norm, breakpoints, colors[:, 0])
    g = np.interp(arr_norm, breakpoints, colors[:, 1])
    b = np.interp(arr_norm, breakpoints, colors[:, 2])

    rgba[:, :, 0] = r.astype(np.uint8)
    rgba[:, :, 1] = g.astype(np.uint8)
    rgba[:, :, 2] = b.astype(np.uint8)

    # DYNAMIC ALPHA MASK:
    # Values <= 0.10: Completely transparent (alpha = 0) - removes the solid green blanket over plains/valleys
    # Values 0.10 - 0.30: Gentle ramp from 0 to 120 (low risk slopes, translucent)
    # Values 0.30 - 0.60: Clear alert opacity 120 to 185 (moderate risk slopes)
    # Values >= 0.60: Strong opacity 185 to 225 (high & severe risk slopes pop out sharply)
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

for state_key, cfg in STATES.items():
    tif_path = cfg['tif']
    if not os.path.exists(tif_path):
        continue
    with rasterio.open(tif_path) as src:
        orig_h, orig_w = src.height, src.width
        scale = TARGET_WIDTH / orig_w
        new_w = TARGET_WIDTH
        new_h = int(orig_h * scale)
        data = src.read(1, out_shape=(new_h, new_w), resampling=rasterio.enums.Resampling.average).astype(np.float32)
        nodata_val = src.nodata if src.nodata is not None else -9999.0

    nodata_mask = (data == nodata_val) | ~np.isfinite(data)
    arr_norm = np.clip(data, 0, 1)
    arr_norm[nodata_mask] = 0.0

    rgba = apply_colormap_alpha_taper(arr_norm, nodata_mask)
    out_png = os.path.join(OUT_DIR, f"{state_key}_susceptibility.png")
    img = Image.fromarray(rgba, mode='RGBA')
    img.save(out_png, 'PNG', optimize=True)
    size_kb = os.path.getsize(out_png) / 1024
    
    alpha_ch = rgba[:, :, 3]
    trans_pct = (alpha_ch == 0).sum() / alpha_ch.size * 100
    hazard_pct = (alpha_ch > 80).sum() / alpha_ch.size * 100
    print(f"[{cfg['label']}] Saved {out_png} ({size_kb:.0f} KB) -> {trans_pct:.1f}% transparent base, {hazard_pct:.1f}% hazard highlights")

print("All PNGs regenerated successfully!")
