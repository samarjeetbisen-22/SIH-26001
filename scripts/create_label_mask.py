"""
Rasterize validated Sikkim landslide polygons onto the master UTM modelling grid.
Output: data/processed/labels/landslide_mask.tif
Values: 1 = landslide, 0 = non-landslide
"""
import os
import geopandas as gpd
import rasterio
from rasterio.features import rasterize

DEM_UTM_PATH = "data/processed/dem/utm/sikkim_dem_utm.tif"
LANDSLIDES_PATH = "data/processed/landslides/sikkim_landslides.shp"
OUTPUT_MASK_PATH = "data/processed/labels/landslide_mask.tif"

def main():
    print("Loading master UTM grid:", DEM_UTM_PATH)
    with rasterio.open(DEM_UTM_PATH) as src:
        meta = src.meta.copy()
        transform = src.transform
        out_shape = (src.height, src.width)
        crs = src.crs

    print(f"Master Grid: shape={out_shape}, CRS={crs}, res={src.res}")

    print("Loading landslide polygons:", LANDSLIDES_PATH)
    gdf = gpd.read_file(LANDSLIDES_PATH)
    print(f"Loaded {len(gdf)} landslide polygons. Native CRS: {gdf.crs}")

    # Reproject to master grid CRS (EPSG:32645)
    if gdf.crs != crs:
        print(f"Reprojecting polygons from {gdf.crs} to {crs}...")
        gdf = gdf.to_crs(crs)

    # Filter out empty or invalid geometries
    gdf = gdf[gdf.geometry.notnull() & gdf.geometry.is_valid]
    print(f"Valid polygons for rasterization: {len(gdf)}")

    shapes = [(geom, 1) for geom in gdf.geometry]

    print("Rasterizing polygons onto master grid...")
    mask = rasterize(
        shapes=shapes,
        out_shape=out_shape,
        transform=transform,
        fill=0,
        dtype='uint8'
    )

    positive_pixels = (mask == 1).sum()
    total_pixels = mask.size
    print(f"Rasterization complete.")
    print(f"Positive (landslide) pixels: {positive_pixels:,} ({positive_pixels / total_pixels * 100:.2f}%)")
    print(f"Negative (non-landslide) pixels: {(mask == 0).sum():,}")

    os.makedirs(os.path.dirname(OUTPUT_MASK_PATH), exist_ok=True)
    meta.update({
        'dtype': 'uint8',
        'count': 1,
        'nodata': 255  # Distinct nodata so 0 is strictly non-landslide
    })

    with rasterio.open(OUTPUT_MASK_PATH, 'w', **meta) as dst:
        dst.write(mask, 1)

    print(f"Saved landslide label mask to: {OUTPUT_MASK_PATH}")

if __name__ == "__main__":
    main()
