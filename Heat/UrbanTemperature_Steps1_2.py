"""
UrbanTemperature_Steps1_2.py

Step 1 – Match each urban municipality to its nearest *rural* KNMI station.
          A station is considered rural if it does not fall inside any of the
          urban municipalities (>1 000 inh/km²) identified in PreparingHeatData.py.

Step 2 – Download daily maximum (TX) and minimum (TN) temperature from the
          KNMI open-data API (no API key required) and compute daily urban
          temperature surfaces:

              T_urban_max(x, y, t) = T_rural_max(t) + UHImax(x, y) * DAYTIME_UHI_FRACTION
              T_urban_min(x, y, t) = T_rural_min(t) + UHImax(x, y) * NOCTURNAL_UHI_FRACTION

          The two fractions reflect the well-documented asymmetry of the urban
          heat island: in the Netherlands, the nocturnal UHI is approximately
          three times stronger than the daytime UHI (Theeuwes et al. 2017,
          Int. J. Climatol. 37:443-454).  Default values:
              DAYTIME_UHI_FRACTION   = 0.33  (daytime ≈ 1/3 of nocturnal peak)
              NOCTURNAL_UHI_FRACTION = 1.00  (nocturnal ≈ UHImax)

          Because the UHImax formula (2 − SVF − Fveg) captures the morphological
          potential for longwave radiation trapping, which is primarily a nighttime
          mechanism (Oke 1982), setting NOCTURNAL_FRACTION = 1.0 is conservative
          and physically appropriate.

Outputs
-------
  <OUTPUT_DIR>/city_station_match.csv   – city → nearest rural station + distance
  <OUTPUT_DIR>/daily_T_rural.csv        – daily T_rural_max + T_rural_min (°C) per city

  Optional (see WRITE_EXAMPLE_RASTERS):
  <OUTPUT_DIR>/daily_Tmax_rasters/  {city}_{YYYYMMDD}_Tmax.tif
  <OUTPUT_DIR>/daily_Tmin_rasters/  {city}_{YYYYMMDD}_Tmin.tif

References
----------
  Oke (1982) The energetic basis of the urban heat island. Q. J. R. Meteorol. Soc. 108:1-24.
  Theeuwes et al. (2017) Urban heat island intensities in Dutch urban areas.
    Int. J. Climatol. 37:443-454.

Dependencies
------------
    pip install geopandas rasterio numpy pandas requests tqdm
"""

import io
import os
import re
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests
from shapely.geometry import Point
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION – update before running
# ─────────────────────────────────────────────────────────────────────────────
POP_DENSITY_CSV      = "/path/to/Bevolkingsdichtheid2024.csv"
UHI_FINAL_DIR        = "/path/to/uhi_final/"    # UHImax_{city}.tif from step 1
OUTPUT_DIR           = "/path/to/urban_temp/"

START_DATE           = "20230101"               # YYYYMMDD
END_DATE             = "20231231"               # YYYYMMDD

# UHI fractions (see module docstring for rationale)
DAYTIME_UHI_FRACTION   = 0.33   # daytime UHI ≈ 1/3 of nocturnal peak (Theeuwes et al. 2017)
NOCTURNAL_UHI_FRACTION = 1.00   # nocturnal UHI ≈ UHImax (SVF-driven longwave suppression)

WRITE_EXAMPLE_RASTERS = True    # write daily Tmax/Tmin rasters for the first city

KNMI_DAILY_URL = "https://www.daggegevens.knmi.nl/klimatologie/daggegevens"


# ─────────────────────────────────────────────────────────────────────────────
# STEP 0  –  Rebuild urban municipality list
#            (mirrors PreparingHeatData.py so both scripts stay in sync)
# ─────────────────────────────────────────────────────────────────────────────
def load_urban_boundaries(pop_density_csv: str) -> gpd.GeoDataFrame:
    """Return GeoDataFrame of Dutch urban municipalities (>1 000 inh/km²)."""
    wfs_url = (
        "https://service.pdok.nl/cbs/gebiedsindelingen/2024/wfs/v1_0"
        "?request=GetFeature&service=WFS&version=1.1.0"
        "&outputFormat=application%2Fjson"
        "&typeName=gebiedsindelingen:gemeente_gegeneraliseerd"
    )
    print("  Fetching municipal boundaries from PDOK …")
    boundaries = gpd.read_file(wfs_url)

    pop = (
        pd.read_csv(pop_density_csv, sep=";")
        .rename(columns={"Gemeente": "statnaam"})
    )
    merged = boundaries.merge(pop, on="statnaam", how="inner")

    # Municipalities missing from CBS CSV – filled manually
    manual = {"'s-Gravenhage": 6868, "Utrecht": 3991, "Groningen": 1314}
    extra_rows = []
    for name, density in manual.items():
        row = boundaries[boundaries["statnaam"] == name].copy()
        if not row.empty:
            row["Inwonersperkmsqland"] = density
            extra_rows.append(row)

    merged["Inwonersperkmsqland"] = (
        merged["Inwonersperkmsqland"]
        .astype(str).str.replace(" ", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )
    if extra_rows:
        merged = pd.concat([merged] + extra_rows, ignore_index=True)

    urban = merged[merged["Inwonersperkmsqland"] > 1000].copy()
    print(f"  {len(urban)} urban municipalities")
    return urban


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1a  –  Fetch all KNMI station metadata
# ─────────────────────────────────────────────────────────────────────────────
def _parse_station_header(text: str) -> gpd.GeoDataFrame:
    """
    Extract station metadata from KNMI comment block.
    Lines look like:
        # 209:         4.518       52.465      -0.2  IJMOND
    """
    pattern = re.compile(
        r"^#\s+(\d+):\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+(.+)$"
    )
    records = []
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            records.append({
                "station_id":   int(m.group(1)),
                "lon":          float(m.group(2)),
                "lat":          float(m.group(3)),
                "alt_m":        float(m.group(4)),
                "station_name": m.group(5).strip(),
            })
    if not records:
        raise ValueError("No station metadata found in KNMI response.")

    return gpd.GeoDataFrame(
        records,
        geometry=[Point(r["lon"], r["lat"]) for r in records],
        crs="EPSG:4326",
    )


def fetch_knmi_stations() -> gpd.GeoDataFrame:
    """Return a GeoDataFrame of all KNMI daily-climate stations."""
    # One-day request is enough to get the full station header
    r = requests.get(
        KNMI_DAILY_URL,
        params={"stns": "ALL", "vars": "TX", "start": "20240101", "end": "20240101"},
        timeout=60,
    )
    r.raise_for_status()
    gdf = _parse_station_header(r.text)
    print(f"  {len(gdf)} KNMI stations found")
    return gdf


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1b  –  Classify stations as urban / rural
# ─────────────────────────────────────────────────────────────────────────────
def classify_stations(
    stations_gdf: gpd.GeoDataFrame,
    urban_boundaries_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Tag every station as urban (True) or rural (False).
    A station is urban if it falls *within* any urban municipality polygon.
    Uses the dissolved union for efficiency.
    """
    stations_rd = stations_gdf.to_crs("EPSG:28992").copy()
    urban_union = urban_boundaries_gdf.to_crs("EPSG:28992").geometry.union_all()
    stations_rd["is_urban"] = stations_rd.geometry.within(urban_union)

    n_rural  = (~stations_rd["is_urban"]).sum()
    n_urban  = stations_rd["is_urban"].sum()
    print(f"  Station classification: {n_rural} rural, {n_urban} urban")
    return stations_rd


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1c  –  Match each city to its nearest rural station
# ─────────────────────────────────────────────────────────────────────────────
def match_cities_to_stations(
    urban_boundaries_gdf: gpd.GeoDataFrame,
    rural_stations_gdf: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """
    For every urban municipality, find the closest rural KNMI station
    (measured as Euclidean distance between city centroid and station in RD New).

    Returns a DataFrame:
        statnaam | station_id | station_name | distance_km
    """
    cities_rd   = urban_boundaries_gdf.to_crs("EPSG:28992").copy()
    stations_rd = rural_stations_gdf.to_crs("EPSG:28992").copy()

    cities_rd["centroid"] = cities_rd.geometry.centroid

    matches = []
    for _, city in tqdm(cities_rd.iterrows(), total=len(cities_rd),
                        desc="  Matching cities"):
        dists = stations_rd.geometry.distance(city["centroid"])
        nearest = stations_rd.loc[dists.idxmin()]
        matches.append({
            "statnaam":     city["statnaam"],
            "station_id":   int(nearest["station_id"]),
            "station_name": nearest["station_name"],
            "distance_km":  round(float(dists.min()) / 1000, 2),
        })

    return pd.DataFrame(matches)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2a  –  Download daily TX and TN from KNMI
# ─────────────────────────────────────────────────────────────────────────────
def _parse_knmi_data(text: str) -> pd.DataFrame:
    """
    Parse data rows from a KNMI daggegevens response requesting TX:TN.
    Both variables are in 0.1 °C units → divided by 10 to get °C.
    Returns columns: station_id | date | T_rural_max_C | T_rural_min_C
    """
    data_lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if not data_lines:
        return pd.DataFrame(columns=["station_id", "date",
                                     "T_rural_max_C", "T_rural_min_C"])

    df = pd.read_csv(
        io.StringIO("\n".join(data_lines)),
        header=None,
        names=["station_id", "date", "TX", "TN"],
        skipinitialspace=True,
    )
    df["station_id"]      = pd.to_numeric(df["station_id"], errors="coerce").astype("Int64")
    df["date"]            = pd.to_datetime(df["date"].astype(str).str.strip(),
                                           format="%Y%m%d", errors="coerce")
    df["TX"]              = pd.to_numeric(df["TX"], errors="coerce")
    df["TN"]              = pd.to_numeric(df["TN"], errors="coerce")
    df["T_rural_max_C"]   = df["TX"] / 10.0
    df["T_rural_min_C"]   = df["TN"] / 10.0
    return (df.drop(columns=["TX", "TN"])
              .dropna(subset=["station_id", "date"]))


def fetch_knmi_daily_tx_tn(
    station_ids: list,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Download daily TX (max) and TN (min) for the requested stations and period.
    Requests are batched by calendar year to avoid API timeouts.
    Returns a long-format DataFrame: station_id | date | T_rural_max_C | T_rural_min_C
    """
    start    = pd.to_datetime(start_date, format="%Y%m%d")
    end      = pd.to_datetime(end_date,   format="%Y%m%d")
    stns_str = ":".join(str(s) for s in sorted(station_ids))

    frames = []
    for year in tqdm(range(start.year, end.year + 1), desc="  Downloading TX:TN by year"):
        yr_start = max(start, pd.Timestamp(year,  1,  1)).strftime("%Y%m%d")
        yr_end   = min(end,   pd.Timestamp(year, 12, 31)).strftime("%Y%m%d")

        r = requests.get(
            KNMI_DAILY_URL,
            params={"stns": stns_str, "vars": "TX:TN",
                    "start": yr_start, "end": yr_end},
            timeout=180,
        )
        r.raise_for_status()
        frames.append(_parse_knmi_data(r.text))

    if not frames:
        return pd.DataFrame(columns=["station_id", "date",
                                     "T_rural_max_C", "T_rural_min_C"])

    combined = pd.concat(frames, ignore_index=True)
    print(f"  {len(combined):,} station-day records downloaded")
    return combined


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2b  –  Build daily T_rural per city (max + min)
# ─────────────────────────────────────────────────────────────────────────────
def build_city_daily_temp(
    city_station_match: pd.DataFrame,
    tx_tn_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join city–station mapping with the downloaded TX/TN data.
    Returns: statnaam | date | station_id | station_name | T_rural_max_C | T_rural_min_C
    """
    merged = city_station_match.merge(tx_tn_df, on="station_id", how="left")
    for col in ("T_rural_max_C", "T_rural_min_C"):
        n_miss = merged[col].isna().sum()
        if n_miss:
            warnings.warn(f"{n_miss} city-day combinations missing {col}.")
    return merged[["statnaam", "date", "station_id", "station_name",
                   "T_rural_max_C", "T_rural_min_C"]]


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2c  –  Write spatial daily urban Tmax and Tmin rasters  (optional)
# ─────────────────────────────────────────────────────────────────────────────
def _load_uhi(uhi_dir: str, city: str):
    """Load UHImax array and rasterio profile; return (array, profile) or (None, None)."""
    uhi_path = os.path.join(uhi_dir, f"UHImax_{city}.tif")
    if not os.path.exists(uhi_path):
        warnings.warn(f"UHImax raster not found – skipping {city}")
        return None, None
    with rasterio.open(uhi_path) as src:
        arr     = src.read(1).astype(np.float32)
        profile = src.profile.copy()
        nodata  = src.nodata
    if nodata is not None:
        arr = np.where(arr == nodata, np.nan, arr)
    return arr, profile


def compute_daily_urban_temp_rasters(
    city: str,
    date: pd.Timestamp,
    T_rural_max_C: float,
    T_rural_min_C: float,
    uhi_dir: str,
    out_dir_max: str,
    out_dir_min: str,
    daytime_fraction: float   = DAYTIME_UHI_FRACTION,
    nocturnal_fraction: float = NOCTURNAL_UHI_FRACTION,
) -> tuple[str | None, str | None]:
    """
    Write one Tmax and one Tmin raster for a single city-day.

    T_urban_max(x,y) = T_rural_max + UHImax(x,y) * daytime_fraction
    T_urban_min(x,y) = T_rural_min + UHImax(x,y) * nocturnal_fraction

    The asymmetry (daytime < nocturnal) follows Theeuwes et al. (2017):
    nocturnal UHI ≈ 3× daytime UHI for Dutch cities.
    """
    uhi, profile = _load_uhi(uhi_dir, city)
    if uhi is None:
        return None, None

    profile.update(dtype="float32", nodata=np.nan)
    os.makedirs(out_dir_max, exist_ok=True)
    os.makedirs(out_dir_min, exist_ok=True)

    path_max = os.path.join(out_dir_max, f"{city}_{date:%Y%m%d}_Tmax.tif")
    with rasterio.open(path_max, "w", **profile) as dst:
        dst.write((T_rural_max_C + uhi * daytime_fraction).astype(np.float32), 1)

    path_min = os.path.join(out_dir_min, f"{city}_{date:%Y%m%d}_Tmin.tif")
    with rasterio.open(path_min, "w", **profile) as dst:
        dst.write((T_rural_min_C + uhi * nocturnal_fraction).astype(np.float32), 1)

    return path_max, path_min


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Step 0: urban boundaries ─────────────────────────────────────────────
    print("\n[0] Loading urban municipality boundaries …")
    urban_boundaries = load_urban_boundaries(POP_DENSITY_CSV)
    urban_list = urban_boundaries["statnaam"].tolist()

    # ── Step 1: station matching ─────────────────────────────────────────────
    print("\n[1] Matching cities to nearest rural KNMI station …")
    all_stations    = fetch_knmi_stations()
    all_stations    = classify_stations(all_stations, urban_boundaries)
    rural_stations  = all_stations[~all_stations["is_urban"]].copy()
    city_station_match = match_cities_to_stations(urban_boundaries, rural_stations)

    match_path = os.path.join(OUTPUT_DIR, "city_station_match.csv")
    city_station_match.to_csv(match_path, index=False)
    print(f"\n  Saved → {match_path}")
    print(city_station_match.to_string(index=False))

    # ── Step 2: download daily TX + TN ──────────────────────────────────────
    print(f"\n[2] Downloading daily TX and TN  ({START_DATE} – {END_DATE}) …")
    unique_ids  = city_station_match["station_id"].unique().tolist()
    tx_tn_df    = fetch_knmi_daily_tx_tn(unique_ids, START_DATE, END_DATE)

    city_daily_temp = build_city_daily_temp(city_station_match, tx_tn_df)
    temp_path = os.path.join(OUTPUT_DIR, "daily_T_rural.csv")
    city_daily_temp.to_csv(temp_path, index=False)
    print(f"  Saved → {temp_path}")

    # Quick summary
    print("\n  Sample (first 5 rows):")
    print(city_daily_temp.head().to_string(index=False))
    print(f"\n  Date range in data : "
          f"{city_daily_temp['date'].min():%Y-%m-%d} – "
          f"{city_daily_temp['date'].max():%Y-%m-%d}")
    print(f"  Cities with data   : "
          f"{city_daily_temp['statnaam'].nunique()} / {len(urban_list)}")
    print(f"  Missing Tmax days  : {city_daily_temp['T_rural_max_C'].isna().sum()}")
    print(f"  Missing Tmin days  : {city_daily_temp['T_rural_min_C'].isna().sum()}")

    # ── Step 2c (optional): write example spatial rasters ────────────────────
    if WRITE_EXAMPLE_RASTERS:
        example_city  = urban_list[0]
        dir_tmax      = os.path.join(OUTPUT_DIR, "daily_Tmax_rasters")
        dir_tmin      = os.path.join(OUTPUT_DIR, "daily_Tmin_rasters")
        rows          = city_daily_temp[city_daily_temp["statnaam"] == example_city]

        print(f"\n[2c] Writing daily Tmax/Tmin rasters for '{example_city}' "
              f"({len(rows)} days) …")
        for _, row in tqdm(rows.iterrows(), total=len(rows), desc=example_city):
            if pd.notna(row["T_rural_max_C"]) and pd.notna(row["T_rural_min_C"]):
                compute_daily_urban_temp_rasters(
                    city          = row["statnaam"],
                    date          = row["date"],
                    T_rural_max_C = row["T_rural_max_C"],
                    T_rural_min_C = row["T_rural_min_C"],
                    uhi_dir       = UHI_FINAL_DIR,
                    out_dir_max   = dir_tmax,
                    out_dir_min   = dir_tmin,
                )
        print(f"  Tmax rasters → {dir_tmax}/")
        print(f"  Tmin rasters → {dir_tmin}/")

    print("\nDone.")
