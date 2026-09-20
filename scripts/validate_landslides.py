import geopandas as gpd
import rasterio
import numpy as np
from rasterio.mask import mask
from shapely.geometry import mapping, box

LANDSLIDES = "data/processed/landslides/sikkim_landslides.shp"

FACTORS = {
    "elevation": "data/processed/dem/utm/sikkim_dem_utm.tif",
    "slope": "data/processed/factors/slope.tif",
    "aspect": "data/processed/factors/aspect.tif",
    "curvature": "data/processed/factors/curvature.tif",
    "twi": "data/processed/hydrology/twi.tif",
    "lithology": "data/processed/factors/lithology.tif",
}

# Load landslide polygons
gdf = gpd.read_file(LANDSLIDES)

print(f"Total landslide polygons: {len(gdf)}")

# Get modelling CRS and DEM bounds
with rasterio.open(FACTORS["elevation"]) as src:
    raster_crs = src.crs
    raster_bounds = src.bounds

# Reproject landslides to modelling CRS
gdf = gdf.to_crs(raster_crs)

dem_box = box(
    raster_bounds.left,
    raster_bounds.bottom,
    raster_bounds.right,
    raster_bounds.top,
)

inside_count = 0
valid_count = 0

for idx, row in gdf.iterrows():

    if row.geometry is None or row.geometry.is_empty:
        continue

    # Does the landslide intersect the DEM?
    if not row.geometry.intersects(dem_box):
        continue

    inside_count += 1

    geom = [mapping(row.geometry)]

    all_valid = True

    for name, path in FACTORS.items():

        with rasterio.open(path) as src:

            data, _ = mask(
                src,
                geom,
                crop=True,
                filled=False
            )

            values = data[0]

            # Masked array → only valid pixels
            valid_values = values.compressed()

            if len(valid_values) == 0:
                all_valid = False
                break

            # Remove NaN / infinite values
            valid_values = valid_values[np.isfinite(valid_values)]

            if len(valid_values) == 0:
                all_valid = False
                break

    if all_valid:
        valid_count += 1

print()
print("======================================")
print("LANDSLIDE VALIDATION")
print("======================================")
print(f"Total polygons              : {len(gdf)}")
print(f"Intersecting DEM             : {inside_count}")
print(f"With all 6 factors valid    : {valid_count}")
print(f"Excluded                     : {inside_count - valid_count}")
print("======================================")
