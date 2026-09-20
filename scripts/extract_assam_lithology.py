"""
Extract lithology for Assam study area from Pan-NER GeoPackage.
Clips data/processed/lithology/pan_ner_lithology.gpkg to Assam bounding box.
Outputs:
- data/processed/lithology/assam/assam_lithology.gpkg
- data/processed/results/assam/lith_id_map.json
- data/processed/results/assam/assam_lithology_map.png
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import box
import warnings
warnings.filterwarnings('ignore')

# Bounding box encompassing Assam landslide event clusters
ASM_BBOX = (89.8, 24.3, 95.1, 27.4) # (minx, miny, maxx, maxy)
ASM_BOX = box(*ASM_BBOX)

print("=" * 60)
print("Assam Lithology Extraction")
print("=" * 60)

lith_path = "data/processed/lithology/pan_ner_lithology.gpkg"
print(f"Loading: {lith_path}")
lith = gpd.read_file(lith_path)

if lith.crs.to_epsg() != 4326:
    lith = lith.to_crs(epsg=4326)

assam_lith = lith.clip(ASM_BOX)
print(f"Features within Assam bbox: {len(assam_lith)}")

col = 'lith_group' if 'lith_group' in assam_lith.columns else 'GLG'
print(f"Lithology formations present:")
print(assam_lith[col].value_counts().to_string())

os.makedirs("data/processed/lithology/assam", exist_ok=True)
out_gpkg = "data/processed/lithology/assam/assam_lithology.gpkg"
assam_lith.to_file(out_gpkg, driver="GPKG")
print(f"Saved: {out_gpkg}")

groups = sorted(assam_lith[col].dropna().unique())
lith_id_map = {g: i + 1 for i, g in enumerate(groups)}
lith_id_map['NoData'] = 0

os.makedirs("data/processed/results/assam", exist_ok=True)
with open("data/processed/results/assam/lith_id_map.json", "w") as f:
    json.dump(lith_id_map, f, indent=2)
print("Saved lith_id_map.json")

# Map Visualization
fig, ax = plt.subplots(figsize=(13, 7))
groups_present = assam_lith[col].dropna().unique()
colors = plt.cm.tab20(np.linspace(0, 1, max(len(groups_present), 1)))
color_map = {g: colors[i] for i, g in enumerate(groups_present)}

for group, gdf in assam_lith.groupby(col):
    gdf.plot(ax=ax, color=color_map.get(group, 'gray'), label=group, alpha=0.7)

events_path = "data/raw/landslides/assam_events.csv"
if os.path.exists(events_path):
    events = pd.read_csv(events_path)
    ax.scatter(events['longitude'], events['latitude'], c='red', s=22, zorder=5,
               edgecolors='black', linewidths=0.6, alpha=0.9,
               label=f'Historical Landslides (n={len(events)})')

ax.set_xlim(ASM_BBOX[0], ASM_BBOX[2])
ax.set_ylim(ASM_BBOX[1], ASM_BBOX[3])
ax.set_title("Assam — Regional Geology & Historical Landslide Events (n=105)",
             fontsize=13, fontweight='bold')
ax.set_xlabel("Longitude (°E)")
ax.set_ylabel("Latitude (°N)")

# Annotate critical corridors
ax.annotate("Guwahati Urban Hills\n(Kamrup Corridor)", xy=(91.75, 26.2), fontsize=8,
            color='navy', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='lightyellow', alpha=0.85))
ax.annotate("Dima Hasao / Haflong\nRailway Section", xy=(93.0, 25.15), fontsize=8,
            color='darkred', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffe6e6', alpha=0.85))
ax.annotate("Barak Valley\n(Karimganj / Hailakandi)", xy=(92.5, 24.6), fontsize=8,
            color='#663300', style='italic',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#f0f0f0', alpha=0.85))

handles = [mpatches.Patch(color=color_map[g], label=g) for g in groups_present if g in color_map]
if os.path.exists(events_path):
    handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
                              markeredgecolor='black', markersize=7,
                              label=f'Events (n={len(events)})'))
ax.legend(handles=handles, loc='upper right', fontsize=8, title='Lithology')
ax.grid(True, alpha=0.3)

out_png = "data/processed/results/assam/assam_lithology_map.png"
plt.tight_layout()
plt.savefig(out_png, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved geology map: {out_png}")
print("Assam lithology extraction complete.")
