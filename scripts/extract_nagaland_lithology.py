"""
Extract lithology for Nagaland study area from the Pan-NER GeoPackage.
Uses the already-processed pan_ner_lithology.gpkg, clips to Nagaland bounds,
and saves a Nagaland-specific GeoPackage.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from shapely.geometry import box

# Nagaland bounding box (with buffer)
NAG_BBOX = (93.5, 25.1, 95.2, 27.0)  # (minx, miny, maxx, maxy)
NAG_BOX = box(*NAG_BBOX)

print("=" * 60)
print("Nagaland Lithology Extraction")
print("=" * 60)

# Load pan-NER lithology
lith_path = "data/processed/lithology/pan_ner_lithology.gpkg"
print(f"Loading: {lith_path}")
lith = gpd.read_file(lith_path)
print(f"  Total features: {len(lith)}")
print(f"  CRS: {lith.crs}")
print(f"  Columns: {lith.columns.tolist()}")

# Reproject to WGS84 if needed
if lith.crs.to_epsg() != 4326:
    lith = lith.to_crs(epsg=4326)

# Clip to Nagaland
nagaland_lith = lith.clip(NAG_BOX)
print(f"\nAfter clip to Nagaland bbox:")
print(f"  Features: {len(nagaland_lith)}")

if len(nagaland_lith) == 0:
    print("⚠ No lithology features found in Nagaland bbox!")
    print("Checking original bounds:", lith.total_bounds)
else:
    print(f"  Lithology groups present:")
    if 'lith_group' in nagaland_lith.columns:
        print(nagaland_lith['lith_group'].value_counts().to_string())
    elif 'GLG' in nagaland_lith.columns:
        print(nagaland_lith['GLG'].value_counts().head(20).to_string())

# Save Nagaland lithology
os.makedirs("data/processed/lithology/nagaland", exist_ok=True)
out_gpkg = "data/processed/lithology/nagaland/nagaland_lithology.gpkg"
nagaland_lith.to_file(out_gpkg, driver="GPKG")
print(f"\nSaved: {out_gpkg}")

# Build lith_id encoding
if 'lith_group' in nagaland_lith.columns:
    groups = sorted(nagaland_lith['lith_group'].dropna().unique())
elif 'GLG' in nagaland_lith.columns:
    groups = sorted(nagaland_lith['GLG'].dropna().unique())
else:
    groups = []

lith_id_map = {g: i+1 for i, g in enumerate(groups)}
lith_id_map['NoData'] = 0
print("\nLithology ID mapping:")
for k, v in lith_id_map.items():
    print(f"  {v}: {k}")

import json
os.makedirs("data/processed/results/nagaland", exist_ok=True)
with open("data/processed/results/nagaland/lith_id_map.json", "w") as f:
    json.dump(lith_id_map, f, indent=2)
print("Saved lith_id_map.json")

# Map susceptibility ratings (inherited from Sikkim pipeline)
susceptibility_map = {
    'Neogene Sedimentary': 5,
    'Quaternary': 1,
    'Tertiary Flysch': 5,
    'Precambrian Metamorphic': 4,
    'Paleozoic Sedimentary': 3,
    'Mesozoic Sedimentary': 3,
    'Igneous Intrusive': 2,
    'Igneous Volcanic': 2,
    'Ophiolite': 4,
    'Alluvium': 1,
    'NoData': 0,
}

# Visualization
if len(nagaland_lith) > 0:
    fig, ax = plt.subplots(figsize=(10, 8))
    
    col = 'lith_group' if 'lith_group' in nagaland_lith.columns else 'GLG'
    groups_present = nagaland_lith[col].dropna().unique()
    colors = plt.cm.tab20(np.linspace(0, 1, max(len(groups_present), 1)))
    color_map = {g: colors[i] for i, g in enumerate(groups_present)}
    
    for group, gdf in nagaland_lith.groupby(col):
        gdf.plot(ax=ax, color=color_map.get(group, 'gray'), label=group, alpha=0.7)
    
    # Plot event points
    events = pd.read_csv("data/raw/landslides/nagaland_events.csv")
    ax.scatter(events['longitude'], events['latitude'], c='red', s=20, zorder=5, 
               alpha=0.8, label=f'Landslide events (n={len(events)})')
    
    ax.set_xlim(NAG_BBOX[0], NAG_BBOX[2])
    ax.set_ylim(NAG_BBOX[1], NAG_BBOX[3])
    ax.set_title("Nagaland — Lithology & Landslide Events", fontsize=14, fontweight='bold')
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    
    # Add NH routes annotation
    ax.annotate("NH-29/NH-2 corridor", xy=(94.2, 25.8), fontsize=9,
                color='navy', style='italic',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='lightyellow', alpha=0.8))
    
    handles = [mpatches.Patch(color=color_map[g], label=g) for g in groups_present if g in color_map]
    handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
                              markersize=8, label=f'Events (n={len(events)})'))
    ax.legend(handles=handles, loc='lower right', fontsize=7, title='Lithology')
    
    ax.grid(True, alpha=0.3)
    out_png = "data/processed/results/nagaland/nagaland_lithology_map.png"
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved map: {out_png}")

print("\n✅ Nagaland lithology extraction complete!")
