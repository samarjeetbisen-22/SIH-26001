"""
Extract and classify regional lithology for the entire Pan-NER region
(Assam, Arunachal Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura)
from the USGS South Asia Geologic Map dataset.
Outputs:
  - GeoPackage: data/processed/lithology/pan_ner_lithology.gpkg
  - Map: data/processed/results/pan_ner_lithology_map.png
"""
import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

SOURCE_SHP = "data/raw/lithology/geo8apg/geo8apg.shp"
OUT_GPKG = "data/processed/lithology/pan_ner_lithology.gpkg"
OUT_PNG = "data/processed/results/pan_ner_lithology_map.png"

# Pan-NER Bounding Box [min_lon, min_lat, max_lon, max_lat]
BBOX = [88.0, 21.5, 97.5, 29.5]

# Comprehensive geological grouping for landslide susceptibility
LITHOLOGY_LOOKUP = {
    'Q':    {'id': 1, 'name': 'Quaternary Alluvium / Unconsolidated', 'susceptibility': 'Low (Flat)', 'color': '#f5f5dc'},
    'N':    {'id': 2, 'name': 'Neogene Sedimentary (Siwalik / Surma)', 'susceptibility': 'Very High', 'color': '#d95f02'},
    'Ts':   {'id': 3, 'name': 'Tertiary Sedimentary Flysch (Disang/Barail)', 'susceptibility': 'Very High', 'color': '#e7298a'},
    'Pg':   {'id': 4, 'name': 'Paleogene Sedimentary Formations', 'susceptibility': 'High', 'color': '#7570b3'},
    'pC':   {'id': 5, 'name': 'Precambrian Crystalline / Gneiss Complex', 'susceptibility': 'Moderate', 'color': '#1b9e77'},
    'MzPz': {'id': 6, 'name': 'Mesozoic-Paleozoic Metasediments', 'susceptibility': 'High', 'color': '#e6ab02'},
    'Pzu':  {'id': 7, 'name': 'Upper Paleozoic Formations', 'susceptibility': 'Moderate', 'color': '#a6761d'},
    'Pz':   {'id': 8, 'name': 'Paleozoic Metamorphic Formations', 'susceptibility': 'Moderate', 'color': '#66a61e'},
    'Ki':   {'id': 9, 'name': 'Cretaceous Igneous Intrusives', 'susceptibility': 'Low-Moderate', 'color': '#386cb0'},
    'Mi':   {'id': 10, 'name': 'Mesozoic Igneous / Ophiolite Belt', 'susceptibility': 'Moderate-High', 'color': '#f0027f'},
    'Tv':   {'id': 11, 'name': 'Tertiary Volcanics / Basalts', 'susceptibility': 'Low', 'color': '#4daf4a'},
    'Other':{'id': 12, 'name': 'Other Metamorphic / Sedimentary Formations', 'susceptibility': 'Moderate', 'color': '#999999'}
}

def get_lith_info(glg):
    glg_clean = str(glg).strip()
    return LITHOLOGY_LOOKUP.get(glg_clean, LITHOLOGY_LOOKUP['Other'])

def main():
    print("================================================================================")
    print("        PAN-NER REGIONAL LITHOLOGY EXTRACTION & MAPPING")
    print("================================================================================")

    print(f"Loading USGS South Asia Geology layer: {SOURCE_SHP}")
    gdf = gpd.read_file(SOURCE_SHP)
    print(f"Total source polygons: {len(gdf)}")

    # Spatial clip using bounding box
    print(f"Clipping to Pan-NER extent: {BBOX}...")
    ner_gdf = gdf.cx[BBOX[0]:BBOX[2], BBOX[1]:BBOX[3]].copy()
    print(f"Extracted {len(ner_gdf)} geological polygons intersecting the Northeast.")

    # Filter out water bodies (H2O)
    ner_gdf = ner_gdf[~ner_gdf['GLG'].str.upper().isin(['H2O', 'H20'])].copy()

    # Assign lithology group attributes
    ner_gdf['lith_id'] = ner_gdf['GLG'].apply(lambda g: get_lith_info(g)['id'])
    ner_gdf['lith_name'] = ner_gdf['GLG'].apply(lambda g: get_lith_info(g)['name'])
    ner_gdf['susceptibility_class'] = ner_gdf['GLG'].apply(lambda g: get_lith_info(g)['susceptibility'])
    ner_gdf['color'] = ner_gdf['GLG'].apply(lambda g: get_lith_info(g)['color'])

    print("\nRegional Lithological Unit Breakdown:")
    print(ner_gdf['lith_name'].value_counts())

    # Save to GeoPackage
    os.makedirs(os.path.dirname(OUT_GPKG), exist_ok=True)
    ner_gdf.to_file(OUT_GPKG, layer="pan_ner_lithology", driver="GPKG")
    print(f"\nSaved regional lithology GeoPackage to: {OUT_GPKG}")

    # Render Regional Map
    print(f"Rendering regional lithology map to: {OUT_PNG}")
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)

    fig, ax = plt.subplots(figsize=(15, 9), dpi=300)

    # Plot polygons by lithology group
    legend_patches = []
    for glg, info in LITHOLOGY_LOOKUP.items():
        sub = ner_gdf[ner_gdf['lith_id'] == info['id']]
        if len(sub) == 0:
            continue
        sub.plot(ax=ax, color=info['color'], edgecolor='black', linewidth=0.3, alpha=0.85)
        patch = mpatches.Patch(facecolor=info['color'], edgecolor='black', lw=0.5,
                               label=f"{info['name']} ({info['susceptibility']})")
        legend_patches.append(patch)

    ax.set_title('Pan-NER Regional Geology & Lithological Formations — All 8 States\n'
                 'USGS South Asia Geological Map (Standardized for Regional Landslide Modeling)',
                 fontsize=13, fontweight='bold', pad=14)
    ax.set_xlabel('Longitude (°E)', fontsize=11)
    ax.set_ylabel('Latitude (°N)', fontsize=11)
    ax.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.6)
    ax.set_xlim([88.0, 97.5])
    ax.set_ylim([21.5, 29.5])

    ax.legend(handles=legend_patches, loc='upper left', frameon=True, fontsize=8.5,
              title="Lithological Formations & Inherent Susceptibility", title_fontsize=9.5)

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=300)
    plt.close()
    print(f"Saved regional lithology map visualization to: {OUT_PNG}")

if __name__ == '__main__':
    main()

