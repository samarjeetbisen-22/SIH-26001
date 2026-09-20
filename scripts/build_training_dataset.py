"""
Extract pixel-level training dataset for Sikkim 6-factor Landslide Susceptibility Model.
Uses all 3,106 valid positive landslide pixels and samples an equal number of valid negative pixels.
Output: data/processed/training/sikkim_training.csv
"""
import os
import rasterio
import numpy as np
import pandas as pd

FACTOR_PATHS = {
    'elevation': 'data/processed/dem/utm/sikkim_dem_utm.tif',
    'slope': 'data/processed/factors/slope.tif',
    'aspect': 'data/processed/factors/aspect.tif',
    'curvature': 'data/processed/factors/curvature.tif',
    'twi': 'data/processed/hydrology/twi.tif',
    'lithology': 'data/processed/factors/lithology.tif'
}
LABEL_PATH = 'data/processed/labels/landslide_mask.tif'
OUTPUT_CSV = 'data/processed/training/sikkim_training.csv'
REPORT_JSON = 'data/processed/training/training_report_sikkim.json'

def main():
    print("--- STEP 3: BUILDING SIKKIM TRAINING DATASET ---")
    
    # 1. Read label mask and master georeference
    with rasterio.open(LABEL_PATH) as src:
        labels = src.read(1)
        transform = src.transform
        crs = src.crs
        height, width = labels.shape

    # 2. Read factors and construct valid mask
    factor_arrays = {}
    valid_mask = np.ones((height, width), dtype=bool)

    for name, path in FACTOR_PATHS.items():
        print(f"Reading {name} from {path}...")
        with rasterio.open(path) as src:
            arr = src.read(1)
            nd = src.nodata
            if nd is not None:
                valid_mask &= (arr != nd)
            if np.issubdtype(arr.dtype, np.floating):
                valid_mask &= ~np.isnan(arr)
            factor_arrays[name] = arr

    # 3. Separate positive and negative pixel coordinates
    pos_indices = np.where((labels == 1) & valid_mask)
    neg_indices = np.where((labels == 0) & valid_mask)

    n_pos = len(pos_indices[0])
    n_neg_total = len(neg_indices[0])

    print(f"\nTotal valid positive pixels: {n_pos:,}")
    print(f"Total valid negative pixels: {n_neg_total:,}")

    # Randomly sample equal number of negatives for balanced training (1:1 ratio)
    np.random.seed(42)
    sample_neg_idx = np.random.choice(n_neg_total, size=n_pos, replace=False)

    sampled_neg_rows = neg_indices[0][sample_neg_idx]
    sampled_neg_cols = neg_indices[1][sample_neg_idx]

    # Combine positive and negative samples
    all_rows = np.concatenate([pos_indices[0], sampled_neg_rows])
    all_cols = np.concatenate([pos_indices[1], sampled_neg_cols])
    targets = np.concatenate([np.ones(n_pos, dtype=int), np.zeros(n_pos, dtype=int)])

    # Compute spatial UTM coordinates
    xs, ys = rasterio.transform.xy(transform, all_rows, all_cols)

    # 4. Extract feature values
    df_data = {
        'row': all_rows,
        'col': all_cols,
        'x': xs,
        'y': ys,
        'elevation': factor_arrays['elevation'][all_rows, all_cols],
        'slope': factor_arrays['slope'][all_rows, all_cols],
        'aspect': factor_arrays['aspect'][all_rows, all_cols],
        'curvature': factor_arrays['curvature'][all_rows, all_cols],
        'twi': factor_arrays['twi'][all_rows, all_cols],
        'lithology': factor_arrays['lithology'][all_rows, all_cols].astype(int),
        'target': targets
    }

    df = pd.DataFrame(df_data)
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved training dataset to: {OUTPUT_CSV}")
    print(f"Dataset shape: {df.shape}")
    print("\nFeature Summary:")
    print(df[['elevation', 'slope', 'aspect', 'curvature', 'twi', 'lithology', 'target']].describe().round(2))

    # Save summary report
    import json
    report = {
        'total_samples': len(df),
        'positive_samples': int(n_pos),
        'negative_samples': int(n_pos),
        'features': list(FACTOR_PATHS.keys()),
        'crs': str(crs),
        'feature_stats': df[['elevation', 'slope', 'aspect', 'curvature', 'twi']].describe().to_dict()
    }
    with open(REPORT_JSON, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Summary report saved to: {REPORT_JSON}")

if __name__ == "__main__":
    main()
