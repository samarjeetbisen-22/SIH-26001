"""
Generate full-area continuous landslide susceptibility map for Sikkim using the trained 6-factor XGBoost model.
Outputs:
  - GeoTIFF: data/processed/results/sikkim_susceptibility_6factor.tif
  - Rendered PNG: data/processed/results/sikkim_susceptibility_6factor.png
"""
import os
import pickle
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch

MODEL_PATH = "models/trained_model_sikkim_6factors.pkl"
FACTOR_PATHS = {
    'elevation': 'data/processed/dem/utm/sikkim_dem_utm.tif',
    'slope': 'data/processed/factors/slope.tif',
    'aspect': 'data/processed/factors/aspect.tif',
    'curvature': 'data/processed/factors/curvature.tif',
    'twi': 'data/processed/hydrology/twi.tif',
    'lithology': 'data/processed/factors/lithology.tif'
}
OUTPUT_TIF = "data/processed/results/sikkim_susceptibility_6factor.tif"
OUTPUT_PNG = "data/processed/results/sikkim_susceptibility_6factor.png"

def main():
    print("--- STEP 5: PREDICTING FULL-AREA SUSCEPTIBILITY MAP ---")
    
    # 1. Load Model
    print(f"Loading trained model: {MODEL_PATH}")
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    # 2. Load Factor Rasters
    meta = None
    factor_data = {}
    valid_mask = None
    shape = None

    for name, path in FACTOR_PATHS.items():
        print(f"Reading {name}...")
        with rasterio.open(path) as src:
            if meta is None:
                meta = src.meta.copy()
                shape = (src.height, src.width)
                valid_mask = np.ones(shape, dtype=bool)

            arr = src.read(1)
            nd = src.nodata
            if nd is not None:
                valid_mask &= (arr != nd)
            if np.issubdtype(arr.dtype, np.floating):
                valid_mask &= ~np.isnan(arr)

            factor_data[name] = arr

    total_pixels = valid_mask.size
    valid_count = valid_mask.sum()
    print(f"Grid shape: {shape}, Total pixels: {total_pixels:,}")
    print(f"Valid pixels for prediction: {valid_count:,} ({valid_count/total_pixels*100:.1f}%)")

    # 3. Predict Probabilities
    # Construct feature matrix for valid pixels
    feature_matrix = np.column_stack([
        factor_data['elevation'][valid_mask],
        factor_data['slope'][valid_mask],
        factor_data['aspect'][valid_mask],
        factor_data['curvature'][valid_mask],
        factor_data['twi'][valid_mask],
        factor_data['lithology'][valid_mask].astype(int)
    ])

    print("Running model inference across full study area...")
    probs = model.predict_proba(feature_matrix)[:, 1]

    # 4. Construct Output Susceptibility Raster
    susceptibility_raster = np.full(shape, fill_value=-9999.0, dtype=np.float32)
    susceptibility_raster[valid_mask] = probs.astype(np.float32)

    print("Susceptibility statistics across valid pixels:")
    print(f"  Min:    {probs.min():.4f}")
    print(f"  Max:    {probs.max():.4f}")
    print(f"  Mean:   {probs.mean():.4f}")
    print(f"  Median: {np.median(probs):.4f}")
    print(f"  Std:    {probs.std():.4f}")

    # Risk class breakdown:
    # Very Low: 0.0 - 0.2, Low: 0.2 - 0.4, Moderate: 0.4 - 0.6, High: 0.6 - 0.8, Very High: 0.8 - 1.0
    c_vlow = (probs < 0.2).sum()
    c_low = ((probs >= 0.2) & (probs < 0.4)).sum()
    c_mod = ((probs >= 0.4) & (probs < 0.6)).sum()
    c_high = ((probs >= 0.6) & (probs < 0.8)).sum()
    c_vhigh = (probs >= 0.8).sum()

    print("\nZonation Distribution:")
    print(f"  Very Low  (0.0-0.2): {c_vlow:,} ({c_vlow/valid_count*100:.1f}%)")
    print(f"  Low       (0.2-0.4): {c_low:,} ({c_low/valid_count*100:.1f}%)")
    print(f"  Moderate  (0.4-0.6): {c_mod:,} ({c_mod/valid_count*100:.1f}%)")
    print(f"  High      (0.6-0.8): {c_high:,} ({c_high/valid_count*100:.1f}%)")
    print(f"  Very High (0.8-1.0): {c_vhigh:,} ({c_vhigh/valid_count*100:.1f}%)")

    # 5. Save GeoTIFF
    os.makedirs(os.path.dirname(OUTPUT_TIF), exist_ok=True)
    meta.update({
        'dtype': 'float32',
        'count': 1,
        'nodata': -9999.0,
        'compress': 'lzw'
    })

    with rasterio.open(OUTPUT_TIF, 'w', **meta) as dst:
        dst.write(susceptibility_raster, 1)
    print(f"\nSaved GeoTIFF susceptibility raster to: {OUTPUT_TIF}")

    # 6. Generate High-Quality Publication Map
    print(f"Rendering visualization to: {OUTPUT_PNG}")
    plt.figure(figsize=(12, 7), dpi=250)

    # Mask nodata for plotting
    plot_data = np.ma.masked_equal(susceptibility_raster, -9999.0)

    cmap = plt.get_cmap('RdYlGn_r').copy()
    cmap.set_bad(color='#dcdcdc')

    im = plt.imshow(plot_data, cmap=cmap, vmin=0.0, vmax=1.0, extent=[
        meta['transform'][2],
        meta['transform'][2] + meta['transform'][0] * meta['width'],
        meta['transform'][5] + meta['transform'][4] * meta['height'],
        meta['transform'][5]
    ])

    cbar = plt.colorbar(im, fraction=0.032, pad=0.04)
    cbar.set_label('Landslide Susceptibility Probability P(Failure)', fontsize=11, fontweight='bold')
    cbar.set_ticks([0.1, 0.3, 0.5, 0.7, 0.9])
    cbar.set_ticklabels(['Very Low (<0.2)', 'Low (0.2-0.4)', 'Moderate (0.4-0.6)', 'High (0.6-0.8)', 'Very High (>0.8)'])

    plt.title('Sikkim Landslide Susceptibility Map (6-Factor XGBoost Model)\nMaster 30m Grid — WGS 84 / UTM Zone 45N (EPSG:32645)',
              fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Easting (meters)', fontsize=10)
    plt.ylabel('Northing (meters)', fontsize=10)
    plt.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.5)

    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=300)
    plt.close()
    print(f"Saved susceptibility map visualization to: {OUTPUT_PNG}")

if __name__ == '__main__':
    main()
