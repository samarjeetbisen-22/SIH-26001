import numpy as np
import rasterio

flow_path = "data/processed/hydrology/flow_accumulation.tif"
slope_path = "data/processed/factors/slope.tif"
output_path = "data/processed/hydrology/twi.tif"

CELL_SIZE = 30.0
NODATA = -9999.0

with rasterio.open(flow_path) as src:
    flow = src.read(1).astype(np.float32)
    profile = src.profile.copy()

with rasterio.open(slope_path) as src:
    slope_deg = src.read(1).astype(np.float32)

valid = (
    (flow > 0) &
    np.isfinite(flow) &
    np.isfinite(slope_deg) &
    (slope_deg > 0) &
    (slope_deg < 89.9)
)

# Flow accumulation is number of cells.
# Convert to contributing area in square metres.
contributing_area = flow * CELL_SIZE * CELL_SIZE

# Degrees -> radians
slope_rad = np.deg2rad(slope_deg)

twi = np.full(flow.shape, NODATA, dtype=np.float32)

twi[valid] = np.log(
    contributing_area[valid] /
    np.tan(slope_rad[valid])
)

twi[~np.isfinite(twi)] = NODATA

profile.update(
    dtype="float32",
    nodata=NODATA,
    compress="lzw"
)

with rasterio.open(output_path, "w", **profile) as dst:
    dst.write(twi, 1)

valid_twi = twi[twi != NODATA]

print("TWI generated successfully")
print(f"Output: {output_path}")
print(f"Valid pixels: {len(valid_twi):,}")
print(f"Minimum TWI: {valid_twi.min():.3f}")
print(f"Maximum TWI: {valid_twi.max():.3f}")
print(f"Mean TWI: {valid_twi.mean():.3f}")
