"""
Extract lithology for Meghalaya study area from the Pan-NER GeoPackage.
Clips data/processed/lithology/pan_ner_lithology.gpkg to Meghalaya bounds.
Outputs:
- data/processed/lithology/meghalaya/meghalaya_lithology.gpkg
- data/processed/results/meghalaya/lith_id_map.json
- data/processed/results/meghalaya/meghalaya_lithology_map.png
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

MEG_BBOX = (89.9, 25.0, 92.6, 26.2) # (minx, miny, maxx, maxy)
MEG_BOX = box(*MEG_BBOX)

print("=" * 60)
print("Meghalaya Lithology Extraction")
print("=" * 60)

lith_path = "data/processed/lithology/pan_ner_lithology.gpkg"
print(f"Loading: {lith_path}")
lith = gpd.read_file(lith_path)
print(f"  Total regional features: {len(lith)}")

if lith.crs.to_epsg() != 4326:
    lith = lith.to_crs(epsg=4326)

meghalaya_lith = lith.clip(MEG_BOX)
print(f"  Features within Meghalaya bbox: {len(meghalaya_lith)}")

col = 'lith_group' if 'lith_group' in meghalaya_lith.columns else 'GLG'
print(f"  Lithology formations present:")
print(meghalaya_lith[col].value_counts().to_string())

os.makedirs("data/processed/lithology/meghalaya", exist_ok=True)
out_gpkg = "data/processed/lithology/meghalaya/meghalaya_lithology.gpkg"
meghalaya_lith.to_file(out_gpkg, driver="GPKG")
print(f"\nSaved: {out_gpkg}")

groups = sorted(meghalaya_lith[col].dropna().unique())
lith_id_map = {g: i + 1 for i, g in enumerate(groups)}
lith_id_map['NoData'] = 0

os.makedirs("data/processed/results/meghalaya", exist_ok=True)
with open("data/processed/results/meghalaya/lith_id_map.json", "w") as f:
    json.dump(lith_id_map, f, indent=2)
print("Saved lith_id_map.json")

# Visualization
if len(meghalaya_lith) > 0:
    fig, ax = plt.subplots(figsize=(11, 7))
    groups_present = meghalaya_lith[col].dropna().unique()
    colors = plt.cm.tab20(np.linspace(0, 1, max(len(groups_present), 1)))
    color_map = {g: colors[i] for i, g in enumerate(groups_present)}

    for group, gdf in meghalaya_lith.groupby(col):
        gdf.plot(ax=ax, color=color_map.get(group, 'gray'), label=group, alpha=0.7)

    events_path = "data/raw/landslides/meghalaya_events.csv"
    if os.path.exists(events_path):
        events = pd.read_csv(events_path)
        ax.scatter(events['longitude'], events['latitude'], c='red', s=25, zorder=5,
                   edgecolors='black', linewidths=0.7, alpha=0.9,
                   label=f'Landslide events (n={len(events)})')

    ax.set_xlim(MEG_BBOX[0], MEG_BBOX[2])
    ax.set_ylim(MEG_BBOX[1], MEG_BBOX[3])
    ax.set_title("Meghalaya — Lithology & Landslide Inventory (Shillong Plateau)",
                 fontsize=13, fontweight='bold')
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # Corridor annotations
    ax.annotate("NH-40 (Guwahati-Shillong)", xy=(91.85, 25.75), fontsize=8,
                color='navy', style='italic',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='lightyellow', alpha=0.8))
    ax.annotate("Cherrapunji / Mawsynram\nEscarpment", xy=(91.6, 25.15), fontsize=8,
                color='darkred', style='italic',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffe6e6', alpha=0.8))

    handles = [mpatches.Patch(color=color_map[g], label=g) for g in groups_present if g in color_map]
    if os.path.exists(events_path):
        handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
                                  markeredgecolor='black', markersize=8,
                                  label=f'Events (n={len(events)})'))
    ax.legend(handles=handles, loc='upper right', fontsize=8, title='Lithology')
    ax.grid(True, alpha=0.3)

    out_png = "data/processed/results/meghalaya/meghalaya_lithology_map.png"
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved map: {out_png}")

print("Meghalaya lithology extraction complete.")

