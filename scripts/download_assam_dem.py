"""
Download 30m DEM tiles for Assam from Copernicus GLO-30 on AWS Open Data.
Covers all 105 recorded landslide events across Assam.
Merges tiles into data/raw/dem/assam/assam_dem_merged.tif.
"""

import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import rasterio
from rasterio.merge import merge
import warnings
warnings.filterwarnings('ignore')

TILES_DIR = "data/raw/dem/assam/tiles"
OUT_FILE  = "data/raw/dem/assam/assam_dem_merged.tif"
os.makedirs(TILES_DIR, exist_ok=True)

# 11 1x1 degree tiles covering all 105 landslide events in Assam
TILES = [
    (24, 92), (24, 93),
    (25, 89), (25, 91), (25, 92), (25, 93),
    (26, 91), (26, 92), (26, 93), (26, 94),
    (27, 94)
]

BASE_URL = "https://copernicus-dem-30m.s3.amazonaws.com"

def download_tile(lat, lon):
    tile_name = f"Copernicus_DSM_COG_10_N{lat:02d}_00_E{lon:03d}_00_DEM"
    url = f"{BASE_URL}/{tile_name}/{tile_name}.tif"
    dest = os.path.join(TILES_DIR, f"{tile_name}.tif")

    if os.path.exists(dest) and os.path.getsize(dest) > 10000000:
        print(f"  [Cached] N{lat:02d}E{lon:03d}")
        return dest

    print(f"  [Downloading] N{lat:02d}E{lon:03d} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; research-bot)"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)
        print(f"  [Finished] N{lat:02d}E{lon:03d} ({os.path.getsize(dest)/1e6:.1f} MB)")
        return dest
    except Exception as e:
        print(f"  [FAILED] N{lat:02d}E{lon:03d}: {e}")
        if os.path.exists(dest):
            os.remove(dest)
        return None

def main():
    if os.path.exists(OUT_FILE) and os.path.getsize(OUT_FILE) > 50000000:
        print(f"Merged DEM already exists: {OUT_FILE}")
        return

    print("=" * 60)
    print(f"Downloading {len(TILES)} Copernicus 30m DEM tiles for Assam")
    print("=" * 60)

    t0 = time.time()
    downloaded_files = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(download_tile, lat, lon) for lat, lon in TILES]
        for f in futures:
            res = f.result()
            if res:
                downloaded_files.append(res)

    print(f"\nDownloaded {len(downloaded_files)} / {len(TILES)} tiles in {time.time()-t0:.1f}s.")

    if len(downloaded_files) < len(TILES):
        print("ERROR: Some tiles failed to download.")
        sys.exit(1)

    print("\nMosaicing tiles into unified GeoTIFF ...")
    src_files = [rasterio.open(f) for f in downloaded_files]
    mosaic, out_transform = merge(src_files)

    out_meta = src_files[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform,
        "compress": "lzw"
    })

    with rasterio.open(OUT_FILE, "w", **out_meta) as dst:
        dst.write(mosaic)

    for src in src_files:
        src.close()

    print(f"Saved merged DEM: {OUT_FILE} ({os.path.getsize(OUT_FILE)/1e6:.1f} MB)")
    print(f"Mosaic shape: {mosaic.shape[1]} x {mosaic.shape[2]}")
    print("DEM preparation complete.")

if __name__ == "__main__":
    main()
