"""
Download SRTM DEM tiles for Meghalaya study area.
Bbox: South=25.0, North=26.2, West=89.9, East=92.6
Uses OpenTopography SRTM GL1 (30m).
Fallback to CGIAR SRTM 90m if required.
"""

import os
import sys
import urllib.request
import shutil

OUT_DIR = "data/raw/dem/meghalaya"
os.makedirs(OUT_DIR, exist_ok=True)

MEG_BOUNDS = {
    "left": 89.9,
    "right": 92.6,
    "bottom": 25.0,
    "top": 26.2,
}

def download_file(url, dest, desc=""):
    print(f"Downloading {desc} ...")
    print(f"  URL: {url}")
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; research-bot)"
        })
        with urllib.request.urlopen(req, timeout=180) as r:
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
        print(f"\n  Saved: {dest} ({os.path.getsize(dest)/1e6:.2f} MB)")
        return True
    except Exception as e:
        print(f"\n  FAILED: {e}")
        return False

def try_opentopo_srtmgl1():
    url = (
        "https://portal.opentopography.org/API/globaldem"
        f"?demtype=SRTMGL1"
        f"&south={MEG_BOUNDS['bottom']}"
        f"&north={MEG_BOUNDS['top']}"
        f"&west={MEG_BOUNDS['left']}"
        f"&east={MEG_BOUNDS['right']}"
        f"&outputFormat=GTiff"
        f"&API_Key=demoapikeyot2022"
    )
    dest = os.path.join(OUT_DIR, "meghalaya_srtm30m.tif")
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        print(f"Already exists: {dest}")
        return dest
    success = download_file(url, dest, "SRTM GL1 30m (OpenTopography)")
    if success and os.path.getsize(dest) > 100000:
        return dest
    if os.path.exists(dest):
        os.remove(dest)
    return None

if __name__ == "__main__":
    merged_out = os.path.join(OUT_DIR, "meghalaya_dem_merged.tif")

    if os.path.exists(merged_out) and os.path.getsize(merged_out) > 100000:
        print(f"Merged DEM already exists: {merged_out}")
        sys.exit(0)

    print("=" * 60)
    print("Meghalaya DEM Download")
    print("=" * 60)
    print(f"Study bbox: {MEG_BOUNDS}")
    print()

    result = try_opentopo_srtmgl1()
    if result:
        print(f"OpenTopography 30m DEM downloaded: {result}")
        shutil.copy(result, merged_out)
        print(f"Copied to: {merged_out}")
        print("SUCCESS: Meghalaya DEM download complete.")
        sys.exit(0)

    print("ERROR: DEM download failed.")
    sys.exit(1)

