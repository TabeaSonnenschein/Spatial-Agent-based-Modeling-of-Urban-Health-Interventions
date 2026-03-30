"""
PreparingHeatData.py
Python translation of the R script for computing Urban Heat Island (UHI) rasters.

Dependencies:
    pip install geopandas rasterio numpy pandas scipy tqdm

"""

import math
import os
import tempfile
import warnings
from concurrent.futures import ProcessPoolExecutor

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask as rasterio_mask
from rasterio.merge import merge as rasterio_merge
from rasterio.transform import from_bounds
from rasterio.warp import reproject
from scipy.ndimage import convolve
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION – update paths before running
# ─────────────────────────────────────────────────────────────────────────────
FVC_PATH        = "/path/to/fvc_test.tif"
SVF_PATH        = "/path/to/merged_svf_all.tif"
POP_DENSITY_CSV = "/path/to/Bevolkingsdichtheid2024.csv"
RURAL_CSV_PATH  = "/path/to/UHImax_allSTN.csv"

SVF_CLIP_DIR    = "/path/to/svf_clipped/"   # clipped SVF per city
UHI_RAW_DIR     = "/path/to/uhi_raw/"       # UHI before rural scaling
UHI_FINAL_DIR   = "/path/to/uhi_final/"     # UHI after rural scaling

NUM_CORES = 8
NX, NY    = 8, 8     # tile grid (8×8 = 64 tiles per city)


# ─────────────────────────────────────────────────────────────────────────────
# 1. MUNICIPAL BOUNDARIES + URBAN FILTER
# ─────────────────────────────────────────────────────────────────────────────
WFS_URL = (
    "https://service.pdok.nl/cbs/gebiedsindelingen/2024/wfs/v1_0"
    "?request=GetFeature&service=WFS&version=1.1.0"
    "&outputFormat=application%2Fjson"
    "&typeName=gebiedsindelingen:gemeente_gegeneraliseerd"
)

print("Fetching municipal boundaries …")
municipal_boundaries = gpd.read_file(WFS_URL)

pop_density = pd.read_csv(POP_DENSITY_CSV, sep=";")
pop_density = pop_density.rename(columns={"Gemeente": "statnaam"})

municipal_merged = municipal_boundaries.merge(pop_density, on="statnaam", how="inner")

# Manually supply density values for municipalities missing from the CSV.
# Values are assigned by name (safer than relying on row order).
missing_data = {
    "'s-Gravenhage": 6868,
    "Utrecht":       3991,
    "Groningen":     1314,
}
missing_rows = []
for name, density in missing_data.items():
    row = municipal_boundaries[municipal_boundaries["statnaam"] == name].copy()
    if not row.empty:
        row["Inwonersperkmsqland"] = density
        missing_rows.append(row)

if missing_rows:
    municipal_missing = pd.concat(missing_rows, ignore_index=True)
    # Ensure Inwonersperkmsqland column exists in municipal_merged
    if "Inwonersperkmsqland" not in municipal_merged.columns:
        municipal_merged["Inwonersperkmsqland"] = np.nan

    # Normalise the column (remove thousands-separator spaces, cast to float)
    municipal_merged["Inwonersperkmsqland"] = (
        municipal_merged["Inwonersperkmsqland"]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

    municipal_merged = pd.concat([municipal_merged, municipal_missing], ignore_index=True)
else:
    municipal_merged["Inwonersperkmsqland"] = (
        municipal_merged["Inwonersperkmsqland"]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

# Keep only urban municipalities (>1 000 inhabitants per km²)
municipal_boundaries = municipal_merged[
    municipal_merged["Inwonersperkmsqland"] > 1000
].copy()

urban_list = municipal_boundaries["statnaam"].tolist()
print(f"Urban municipalities found: {len(urban_list)}")

del municipal_merged, pop_density


# ─────────────────────────────────────────────────────────────────────────────
# 2. CLIP SVF RASTER TO EACH CITY
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs(SVF_CLIP_DIR, exist_ok=True)

print("Clipping SVF raster per city …")
with rasterio.open(SVF_PATH) as src_svf:
    raster_crs = src_svf.crs

    for city in tqdm(urban_list, desc="Clipping SVF"):
        boundary = municipal_boundaries[municipal_boundaries["statnaam"] == city]
        boundary_proj = boundary.to_crs(raster_crs)
        shapes = [geom.__geo_interface__ for geom in boundary_proj.geometry]

        try:
            clipped, transform = rasterio_mask(src_svf, shapes, crop=True)
            meta = src_svf.meta.copy()
            meta.update(
                height=clipped.shape[1],
                width=clipped.shape[2],
                transform=transform,
            )
            out_path = os.path.join(SVF_CLIP_DIR, f"{city}.tif")
            with rasterio.open(out_path, "w", **meta) as dst:
                dst.write(clipped)
        except Exception as exc:
            warnings.warn(f"Could not clip '{city}': {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. TILE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def circular_kernel(radius_cells: int) -> np.ndarray:
    """Binary circular kernel with the given radius expressed in cells."""
    d = 2 * radius_cells + 1
    cy = cx = radius_cells
    y, x = np.ogrid[:d, :d]
    return ((x - cx) ** 2 + (y - cy) ** 2 <= radius_cells ** 2).astype(np.float64)


def split_bounds(left, bottom, right, top, nx, ny):
    """Yield (xmin, ymin, xmax, ymax) for each cell of an nx×ny grid."""
    dx = (right - left) / nx
    dy = (top - bottom) / ny
    for row in range(ny):
        for col in range(nx):
            yield (
                left  + col       * dx,
                bottom + row       * dy,
                left  + (col + 1) * dx,
                bottom + (row + 1) * dy,
            )


def process_tile(args):
    """
    Compute the UHI index for a single tile.

    Equivalent to the R `process_tile` function:
      UHI = (2 - SVF_tile - mean_vegetation_cover) * 1

    Parameters (packed as a tuple for ProcessPoolExecutor.map):
        tile_bounds : (xmin, ymin, xmax, ymax) in the raster CRS
        svf_path    : path to the city-clipped SVF raster
        fvc_path    : path to the fractional vegetation cover raster

    Returns (uhi_array, affine_transform, crs_wkt), or None on failure.
    """
    tile_bounds, svf_path, fvc_path = args
    xmin, ymin, xmax, ymax = tile_bounds

    OFFSET       = 50   # metres – buffer added around each tile
    TARGET_RES   = 5    # metres – FVC is resampled to this resolution
    FOCAL_RADIUS = 50   # metres – radius of the circular focal window

    xmin_e = xmin - OFFSET
    xmax_e = xmax + OFFSET
    ymin_e = ymin - OFFSET
    ymax_e = ymax + OFFSET

    try:
        # ── read SVF tile ────────────────────────────────────────────────────
        with rasterio.open(svf_path) as src:
            svf_crs = src.crs
            win = rasterio.windows.from_bounds(xmin, ymin, xmax, ymax,
                                               transform=src.transform)
            svf_data = src.read(1, window=win).astype(np.float32)
            svf_nodata = src.nodata
            svf_src_transform = src.window_transform(win)

        if svf_nodata is not None:
            svf_data = np.where(svf_data == svf_nodata, np.nan, svf_data)

        # ── read FVC in extended bounds ──────────────────────────────────────
        with rasterio.open(fvc_path) as src:
            fvc_nodata = src.nodata
            fvc_crs    = src.crs
            win_e = rasterio.windows.from_bounds(xmin_e, ymin_e, xmax_e, ymax_e,
                                                 transform=src.transform)
            fvc_raw           = src.read(1, window=win_e).astype(np.float32)
            fvc_raw_transform = src.window_transform(win_e)

        if fvc_nodata is not None:
            fvc_raw = np.where(fvc_raw == fvc_nodata, np.nan, fvc_raw)

        # ── resample FVC to TARGET_RES (nearest-neighbour, same as R "ngb") ──
        new_w = math.ceil((xmax_e - xmin_e) / TARGET_RES)
        new_h = math.ceil((ymax_e - ymin_e) / TARGET_RES)
        dst_transform = from_bounds(xmin_e, ymin_e, xmax_e, ymax_e, new_w, new_h)

        fvc_5m = np.full((new_h, new_w), np.nan, dtype=np.float32)
        reproject(
            source=fvc_raw,
            destination=fvc_5m,
            src_transform=fvc_raw_transform,
            src_crs=fvc_crs,
            dst_transform=dst_transform,
            dst_crs=svf_crs,
            resampling=Resampling.nearest,
            src_nodata=np.nan,
            dst_nodata=np.nan,
        )

        # ── circular focal mean (radius = FOCAL_RADIUS / TARGET_RES cells) ───
        radius_cells = int(FOCAL_RADIUS / TARGET_RES)
        kernel    = circular_kernel(radius_cells)
        nan_mask  = np.isnan(fvc_5m)
        fvc_fill  = np.where(nan_mask, 0.0, fvc_5m.astype(np.float64))
        wt_sum    = convolve((~nan_mask).astype(np.float64), kernel,
                             mode="constant", cval=0.0)
        foc_sum   = convolve(fvc_fill, kernel, mode="constant", cval=0.0)

        with np.errstate(invalid="ignore", divide="ignore"):
            mean_veg = np.where(wt_sum > 0, foc_sum / wt_sum, np.nan)

        # ── crop mean_veg back to the original (un-buffered) tile extent ─────
        c0   = round((xmin - xmin_e) / TARGET_RES)
        r0   = round((ymax_e - ymax) / TARGET_RES)   # rasters are top-down
        t_w  = math.ceil((xmax - xmin) / TARGET_RES)
        t_h  = math.ceil((ymax - ymin) / TARGET_RES)
        c0   = max(0, c0)
        r0   = max(0, r0)
        mean_veg_crop = mean_veg[r0: r0 + t_h, c0: c0 + t_w]

        # ── resample SVF tile to match the 5 m grid ──────────────────────────
        svf_5m = np.full((t_h, t_w), np.nan, dtype=np.float32)
        svf_dst_transform = from_bounds(xmin, ymin, xmax, ymax, t_w, t_h)
        reproject(
            source=svf_data,
            destination=svf_5m,
            src_transform=svf_src_transform,
            src_crs=svf_crs,
            dst_transform=svf_dst_transform,
            dst_crs=svf_crs,
            resampling=Resampling.nearest,
            src_nodata=np.nan,
            dst_nodata=np.nan,
        )

        # ── guard against off-by-one shape mismatches from rounding ──────────
        min_h = min(svf_5m.shape[0], mean_veg_crop.shape[0])
        min_w = min(svf_5m.shape[1], mean_veg_crop.shape[1])
        svf_5m        = svf_5m[:min_h, :min_w]
        mean_veg_crop = mean_veg_crop[:min_h, :min_w]

        UHI = (2.0 - svf_5m - mean_veg_crop).astype(np.float32)

        out_transform = from_bounds(xmin, ymin, xmax, ymax, min_w, min_h)
        return UHI, out_transform, svf_crs.to_wkt()

    except Exception as exc:
        warnings.warn(f"Tile {tile_bounds} failed: {exc}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 4. PROCESS EACH CITY (parallel tile processing)
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs(UHI_RAW_DIR, exist_ok=True)

print("Computing UHI per city …")
for city in tqdm(urban_list, desc="Cities"):
    svf_file = os.path.join(SVF_CLIP_DIR, f"{city}.tif")

    if not os.path.exists(svf_file):
        warnings.warn(f"File not found for: {city}")
        continue

    with rasterio.open(svf_file) as src:
        bounds  = src.bounds
        profile = src.profile

    tile_bounds_list = list(
        split_bounds(bounds.left, bounds.bottom, bounds.right, bounds.top, NX, NY)
    )
    args_list = [(tb, svf_file, FVC_PATH) for tb in tile_bounds_list]

    with ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
        results = list(executor.map(process_tile, args_list))

    results = [r for r in results if r is not None]

    if not results:
        warnings.warn(f"No valid tiles for: {city}")
        continue

    # Write each tile to a temp file, merge, then save the final city raster
    tmp_paths = []
    try:
        for uhi, tf, crs_wkt in results:
            fp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
            fp.close()
            with rasterio.open(
                fp.name, "w",
                driver="GTiff",
                height=uhi.shape[0],
                width=uhi.shape[1],
                count=1,
                dtype=uhi.dtype,
                crs=crs_wkt,
                transform=tf,
                nodata=np.nan,
            ) as dst:
                dst.write(uhi, 1)
            tmp_paths.append(fp.name)

        tile_srcs = [rasterio.open(p) for p in tmp_paths]
        merged, merge_transform = rasterio_merge(tile_srcs)
        for s in tile_srcs:
            s.close()

        out_profile = profile.copy()
        out_profile.update(
            height=merged.shape[1],
            width=merged.shape[2],
            transform=merge_transform,
            count=1,
            dtype=merged.dtype,
            nodata=np.nan,
        )
        out_path = os.path.join(UHI_RAW_DIR, f"{city}.tif")
        with rasterio.open(out_path, "w", **out_profile) as dst:
            dst.write(merged)

        print(f"Processed and saved UHI raster for: {city}")

    finally:
        for p in tmp_paths:
            try:
                os.unlink(p)
            except OSError:
                pass


# ─────────────────────────────────────────────────────────────────────────────
# 5. APPLY RURAL MEASUREMENTS
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs(UHI_FINAL_DIR, exist_ok=True)

rural_df = pd.read_csv(RURAL_CSV_PATH)

print("Applying rural measurements …")
for city in tqdm(urban_list, desc="Rural scaling"):
    uhi_file = os.path.join(UHI_RAW_DIR, f"{city}.tif")
    if not os.path.exists(uhi_file):
        continue

    row = rural_df[rural_df["urban_area"] == city]
    if row.empty:
        continue

    rural_value = float(row["rural"].iloc[0])

    with rasterio.open(uhi_file) as src:
        data    = src.read(1).astype(np.float32)
        profile = src.profile

    data_scaled = data * rural_value

    out_path = os.path.join(UHI_FINAL_DIR, f"UHImax_{city}.tif")
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(data_scaled, 1)

print("Done.")
