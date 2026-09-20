"""
Download SRTM DEM tiles for Nagaland study area.
Tiles needed: N25E093, N25E094, N26E093, N26E094
Uses NASA EarthData / OpenTopography SRTM GL1 (1 arc-second = ~30m).

Falls back to CGIAR SRTM 3-arc-second (90m) if 30m not available.
"""

import os
import sys
import urllib.request
import zipfile
import subprocess

# Output directory
OUT_DIR = "data/raw/dem/nagaland"
os.makedirs(OUT_DIR, exist_ok=True)

# Nagaland bounding box (with small buffer)
NAG_BOUNDS = {
    "left": 93.5,
    "right": 95.2,
    "bottom": 25.1,
    "top": 27.0,
}

def download_file(url, dest, desc=""):
    """Download with progress."""
    print(f"Downloading {desc} ...")
    print(f"  URL: {url}")
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; research-bot)"
        })
        with urllib.request.urlopen(req, timeout=120) as r:
            total = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            chunk = 65536
            with open(dest, "wb") as f:
                while True:
                    data = r.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    downloaded += len(data)
                    if total:
                        pct = downloaded / total * 100
                        print(f"\r  {pct:.1f}% ({downloaded/1e6:.1f} MB / {total/1e6:.1f} MB)", end="", flush=True)
        print(f"\n  Saved: {dest}")
        return True
    except Exception as e:
        print(f"\n  FAILED: {e}")
        return False


def try_opentopo_srtmgl1():
    """
    Try downloading SRTM GL1 (30m) via OpenTopography API.
    Endpoint: https://portal.opentopography.org/API/globaldem
    """
    url = (
        "https://portal.opentopography.org/API/globaldem"
        f"?demtype=SRTMGL1"
        f"&south={NAG_BOUNDS['bottom']}"
        f"&north={NAG_BOUNDS['top']}"
        f"&west={NAG_BOUNDS['left']}"
        f"&east={NAG_BOUNDS['right']}"
        f"&outputFormat=GTiff"
        f"&API_Key=demoapikeyot2022"
    )
    dest = os.path.join(OUT_DIR, "nagaland_srtm30m.tif")
    if os.path.exists(dest):
        print(f"Already exists: {dest}")
        return dest
    success = download_file(url, dest, "SRTM GL1 30m (OpenTopography)")
    if success and os.path.getsize(dest) > 10000:
        return dest
    os.remove(dest) if os.path.exists(dest) else None
    return None


def try_cgiar_srtm():
    """
    Try CGIAR SRTM 90m tiles as fallback.
    Tiles covering Nagaland: srtm_53_07 and srtm_54_07
    """
    tiles = [("53", "07"), ("54", "07")]
    downloaded = []
    for col, row in tiles:
        fname = f"srtm_{col}_{row}.zip"
        dest_zip = os.path.join(OUT_DIR, fname)
        dest_tif = os.path.join(OUT_DIR, fname.replace(".zip", ".tif"))
        if os.path.exists(dest_tif):
            print(f"Already exists: {dest_tif}")
            downloaded.append(dest_tif)
            continue
        url = f"https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/{fname}"
        if download_file(url, dest_zip, f"CGIAR tile {fname}"):
            try:
                with zipfile.ZipFile(dest_zip, "r") as z:
                    tif_names = [n for n in z.namelist() if n.endswith(".tif")]
                    z.extractall(OUT_DIR)
                    for tn in tif_names:
                        src = os.path.join(OUT_DIR, tn)
                        if os.path.exists(src):
                            downloaded.append(src)
                            print(f"  Extracted: {src}")
                os.remove(dest_zip)
            except Exception as e:
                print(f"  Unzip failed: {e}")
    return downloaded


def try_usgs_earthexplorer_hgt():
    """
    Generate synthetic DEM using SRTM HGT tiles from USGS via urllib.
    Note: NASA Earthdata requires login. This is a public mirror attempt.
    """
    tiles = ["N25E093", "N25E094", "N26E093", "N26E094"]
    hgt_files = []
    
    # Try a public mirror
    mirrors = [
        "https://dds.cr.usgs.gov/srtm/version2_1/SRTM1/Region_06/",
        "https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/",
    ]
    
    for tile in tiles:
        fname = f"{tile}.SRTMGL1.hgt.zip"
        dest_hgt = os.path.join(OUT_DIR, tile + ".hgt")
        if os.path.exists(dest_hgt):
            print(f"Already exists: {dest_hgt}")
            hgt_files.append(dest_hgt)
            continue
        
        for mirror in mirrors:
            url = mirror + fname
            dest_zip = os.path.join(OUT_DIR, fname)
            if download_file(url, dest_zip, f"SRTM HGT {tile}"):
                try:
                    with zipfile.ZipFile(dest_zip, "r") as z:
                        z.extractall(OUT_DIR)
                    os.remove(dest_zip)
                    extracted = os.path.join(OUT_DIR, tile + ".hgt")
                    if os.path.exists(extracted):
                        hgt_files.append(extracted)
                        break
                except Exception as e:
                    print(f"  Unzip failed: {e}")
    return hgt_files


def merge_and_clip(input_files, out_path):
    """Use gdalwarp/gdal_merge to merge multiple rasters."""
    import subprocess
    if len(input_files) == 1:
        subprocess.run(
            ["gdal_translate", "-of", "GTiff", input_files[0], out_path],
            check=True
        )
    else:
        cmd = ["gdal_merge.py", "-o", out_path, "-of", "GTiff"] + input_files
        subprocess.run(cmd, check=True)
    print(f"Merged to: {out_path}")


if __name__ == "__main__":
    merged_out = os.path.join(OUT_DIR, "nagaland_dem_merged.tif")

    if os.path.exists(merged_out) and os.path.getsize(merged_out) > 100000:
        print(f"Merged DEM already exists: {merged_out}")
        sys.exit(0)

    print("=" * 60)
    print("Nagaland DEM Download")
    print("=" * 60)
    print(f"Study bbox: {NAG_BOUNDS}")
    print()

    # Attempt 1: OpenTopography GL1 30m
    result = try_opentopo_srtmgl1()
    if result:
        print(f"\n✅ OpenTopography 30m DEM downloaded: {result}")
        # Rename to standard name
        import shutil
        shutil.copy(result, merged_out)
        print(f"Copied to: {merged_out}")
        sys.exit(0)

    # Attempt 2: CGIAR SRTM 90m
    print("\nAttempt 2: CGIAR SRTM 90m ...")
    cgiar_files = try_cgiar_srtm()
    if cgiar_files:
        print(f"\n✅ CGIAR tiles downloaded: {cgiar_files}")
        if len(cgiar_files) > 0:
            merge_and_clip(cgiar_files, merged_out)
            sys.exit(0)

    # Attempt 3: USGS HGT
    print("\nAttempt 3: USGS HGT tiles ...")
    hgt_files = try_usgs_earthexplorer_hgt()
    if hgt_files:
        print(f"\n✅ HGT tiles: {hgt_files}")
        merge_and_clip(hgt_files, merged_out)
        sys.exit(0)

    print("\n❌ All download attempts failed.")
    print("Please manually download SRTM tiles for Nagaland from:")
    print("  https://portal.opentopography.org/raster?opentopoID=OTSRTM.082015.4326.1")
    print("  Bbox: West=93.5, East=95.2, South=25.1, North=27.0")
    print(f"  Save the merged GeoTIFF as: {merged_out}")
    sys.exit(1)
