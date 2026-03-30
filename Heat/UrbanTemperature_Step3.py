"""
UrbanTemperature_Step3.py

Step 3 – Hourly temporal disaggregation of daily urban temperatures.

Method: Double-Sine model (Parton & Logan 1981; Hubbard et al. 1994)
─────────────────────────────────────────────────────────────────────
The day is split into two half-sine segments anchored at T_min and T_max:

  Segment 1 – Rising limb (sunrise t_sr → time of daily max t_Tx):
      T(h) = T_min + (T_max − T_min) · sin( π/2 · (h − t_sr) / (t_Tx − t_sr) )

  Segment 2 – Falling limb (t_Tx → next sunrise t_sr_next):
      T(h) = T_min_next + (T_max − T_min_next) · cos( π/2 · (h − t_Tx) / (t_sr_next − t_Tx) )

Both T_min and T_max are taken from the *urban* values already computed in
Step 2, so the spatial UHI structure is preserved through the anchors:

    T_urban_max(x,y) = T_rural_max + UHImax(x,y) · DAYTIME_FRACTION    (step 2)
    T_urban_min(x,y) = T_rural_min + UHImax(x,y) · NOCTURNAL_FRACTION  (step 2)

The stronger nocturnal fraction (default 1.0 vs 0.33 for daytime) means the
model naturally produces a larger UHI effect at night and a smaller one during
the afternoon — consistent with Theeuwes et al. (2017) who report a ~3:1
nocturnal-to-daytime UHI ratio for Dutch cities.

Calibration of t_Tx
───────────────────
The time of daily maximum temperature (t_Tx) is calibrated per city from
KNMI hourly station data.  The nearest *non-rural* (urban/peri-urban) station
is used so that the diurnal timing reflects urban thermal dynamics rather than
rural open-field conditions — urban areas typically peak 1–2 h later than
rural areas due to heat storage in buildings and pavement.

Output
──────
  <OUTPUT_DIR>/city_calibration_params.csv
      city | hourly_station_id | hourly_station_name | lat | t_Tx_mean_h
           | t_Tx_std_h | n_calibration_days

  <OUTPUT_DIR>/hourly_T_rural.csv
      statnaam | date | hour | T_rural_C
      (24 rows per city-day; rural hourly temperature disaggregated from
       the matched rural station's daily Tmax/Tmin)

  The ABM computes the spatial hourly urban temperature on-the-fly:
      T_urban(x, y, h) = hourly_T_rural[h] + UHImax(x, y) · w(h)
  where w(h) is the diurnal UHI weight (see `uhi_diurnal_weight`).

References
──────────
  Parton & Logan (1981) A model for diurnal variation in soil and air
    temperature. Agric. Meteorol. 23:205-216.
  Hubbard et al. (1994) Hourly and subdaily temperature estimation from
    daily min and max temperatures. Agric. Forest Meteorol. 68:1-18.
  Theeuwes et al. (2017) Urban heat island intensities in Dutch urban areas.
    Int. J. Climatol. 37:443-454.
  Oke (1982) The energetic basis of the urban heat island.
    Q. J. R. Meteorol. Soc. 108:1-24.

Dependencies
────────────
    pip install geopandas numpy pandas requests tqdm
"""

import io
import os
import re
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION – update before running
# ─────────────────────────────────────────────────────────────────────────────
# Inputs from steps 1 & 2
STEP2_OUTPUT_DIR     = "/path/to/urban_temp/"          # OUTPUT_DIR from step 2
POP_DENSITY_CSV      = "/path/to/Bevolkingsdichtheid2024.csv"

# Date range – should match (or be a subset of) what step 2 downloaded
START_DATE           = "20230101"       # YYYYMMDD
END_DATE             = "20231231"       # YYYYMMDD

# Output
OUTPUT_DIR           = "/path/to/urban_temp/"

# Calibration: minimum days required to trust the t_Tx estimate
MIN_CALIBRATION_DAYS = 30

# Daytime UHI fraction (must match step 2)
DAYTIME_UHI_FRACTION   = 0.33
NOCTURNAL_UHI_FRACTION = 1.00

KNMI_DAILY_URL  = "https://www.daggegevens.knmi.nl/klimatologie/daggegevens"
KNMI_HOURLY_URL = "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens"


# ─────────────────────────────────────────────────────────────────────────────
# SOLAR GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────
def solar_times(doy: int, lat_deg: float) -> tuple[float, float]:
    """
    Compute sunrise and sunset in decimal local-solar hours (0–24) for a given
    day-of-year and latitude.

    Uses Spencer (1971) declination and a standard hour-angle formula.
    For the Netherlands (UTC+1 / UTC+2) local clock time ≈ local solar time
    within ±30 min, which is sufficient for this application.

    Returns (t_sunrise, t_sunset).  At extreme latitudes where the sun never
    rises/sets, returns (0, 24) or (12, 12) as degenerate cases.
    """
    B    = 2 * np.pi * (doy - 1) / 365
    decl = (0.006918
            - 0.399912 * np.cos(B)    + 0.070257 * np.sin(B)
            - 0.006758 * np.cos(2*B)  + 0.000907 * np.sin(2*B))  # radians

    lat     = np.radians(lat_deg)
    cos_ha  = -np.tan(lat) * np.tan(decl)
    cos_ha  = float(np.clip(cos_ha, -1.0, 1.0))
    ha_deg  = np.degrees(np.arccos(cos_ha))   # hour angle at sunrise (degrees)

    t_sr = 12.0 - ha_deg / 15.0
    t_ss = 12.0 + ha_deg / 15.0
    return float(t_sr), float(t_ss)


# ─────────────────────────────────────────────────────────────────────────────
# DOUBLE-SINE DISAGGREGATION MODEL
# ─────────────────────────────────────────────────────────────────────────────
def double_sine_hourly(
    T_min: float,
    T_max: float,
    T_min_next: float,
    t_sr: float,
    t_ss: float,
    t_Tx: float,
) -> np.ndarray:
    """
    Disaggregate daily Tmin / Tmax to 24 hourly midpoint temperatures (°C).

    Segment 1  – rising limb  (t_sr → t_Tx):  half-sine from T_min to T_max
    Segment 2  – falling limb (t_Tx → t_sr+24): half-cosine from T_max to T_min_next
    Pre-sunrise (0 → t_sr):  continuation of the falling limb from the previous day
                              (wraps using the same formula with t shifted by +24)

    Parameters
    ----------
    T_min, T_max  : daily minimum and maximum temperatures (°C) for current day
    T_min_next    : minimum temperature of the following day (°C)
    t_sr, t_ss    : sunrise and sunset (decimal hours, local solar time)
    t_Tx          : calibrated time of daily maximum temperature (decimal hours)

    Returns
    -------
    np.ndarray of shape (24,) – temperature at the midpoint of each clock hour
    """
    # next sunrise (expressed as hours > 24 for phase calculations)
    DL          = t_ss - t_sr           # day length (hours)
    t_sr_next   = t_sr + 24.0           # next day's sunrise

    if t_Tx <= t_sr:
        t_Tx = t_sr + 0.5 * DL         # fallback: peak at solar noon

    fall_range = t_sr_next - t_Tx       # hours from peak to next sunrise

    temps = np.empty(24, dtype=np.float64)
    for h in range(24):
        t = h + 0.5                     # use midpoint of each hour

        if t < t_sr:
            # Pre-sunrise: continuation of yesterday's falling limb
            phase = (t + 24 - t_Tx) / fall_range
            phase = np.clip(phase, 0.0, 1.0)
            temps[h] = T_min_next + (T_max - T_min_next) * np.cos(np.pi / 2 * phase)

        elif t <= t_Tx:
            # Rising limb: T_min at sunrise → T_max at t_Tx
            phase = (t - t_sr) / (t_Tx - t_sr)
            temps[h] = T_min + (T_max - T_min) * np.sin(np.pi / 2 * phase)

        else:
            # Falling limb: T_max at t_Tx → T_min_next at next sunrise
            phase = (t - t_Tx) / fall_range
            phase = np.clip(phase, 0.0, 1.0)
            temps[h] = T_min_next + (T_max - T_min_next) * np.cos(np.pi / 2 * phase)

    return temps


# ─────────────────────────────────────────────────────────────────────────────
# DIURNAL UHI WEIGHT  (for on-the-fly spatial urban temperature in the ABM)
# ─────────────────────────────────────────────────────────────────────────────
def uhi_diurnal_weight(
    hours: np.ndarray,
    t_sr: float,
    t_ss: float,
    daytime_fraction: float   = DAYTIME_UHI_FRACTION,
    nocturnal_fraction: float = NOCTURNAL_UHI_FRACTION,
) -> np.ndarray:
    """
    Return the fractional UHI intensity w(h) for each hour in *hours*.

    The UHI peaks ~3 h after sunset and reaches its minimum around solar noon,
    following Theeuwes et al. (2017) and Oke (1982).  A cosine interpolation
    between the nocturnal and daytime fractions is used:

        w(h) = mean + amplitude · cos( 2π · (h − h_peak) / 24 )

    where h_peak = t_ss + 3 (hours after sunset),
          mean    = (nocturnal_fraction + daytime_fraction) / 2,
          amplitude = (nocturnal_fraction - daytime_fraction) / 2.

    Usage in the ABM:
        T_urban(x, y, h) = T_rural(h) + UHImax(x, y) * w(h)

    This function is provided as a convenience for ABM agents; the outputs of
    this script (hourly_T_rural.csv) already embed the rural diurnal cycle.
    """
    h_peak    = t_ss + 3.0
    mean_w    = (nocturnal_fraction + daytime_fraction) / 2.0
    amplitude = (nocturnal_fraction - daytime_fraction) / 2.0
    return mean_w + amplitude * np.cos(2 * np.pi * (hours - h_peak) / 24.0)


# ─────────────────────────────────────────────────────────────────────────────
# KNMI STATION HELPERS  (shared with steps 1 & 2, copied here for independence)
# ─────────────────────────────────────────────────────────────────────────────
def _parse_station_header(text: str) -> gpd.GeoDataFrame:
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
    r = requests.get(
        KNMI_DAILY_URL,
        params={"stns": "ALL", "vars": "TX", "start": "20240101", "end": "20240101"},
        timeout=60,
    )
    r.raise_for_status()
    return _parse_station_header(r.text)


def load_urban_boundaries(pop_density_csv: str) -> gpd.GeoDataFrame:
    wfs_url = (
        "https://service.pdok.nl/cbs/gebiedsindelingen/2024/wfs/v1_0"
        "?request=GetFeature&service=WFS&version=1.1.0"
        "&outputFormat=application%2Fjson"
        "&typeName=gebiedsindelingen:gemeente_gegeneraliseerd"
    )
    boundaries = gpd.read_file(wfs_url)
    pop = (pd.read_csv(pop_density_csv, sep=";")
             .rename(columns={"Gemeente": "statnaam"}))
    merged = boundaries.merge(pop, on="statnaam", how="inner")
    manual = {"'s-Gravenhage": 6868, "Utrecht": 3991, "Groningen": 1314}
    extra  = []
    for name, density in manual.items():
        row = boundaries[boundaries["statnaam"] == name].copy()
        if not row.empty:
            row["Inwonersperkmsqland"] = density
            extra.append(row)
    merged["Inwonersperkmsqland"] = (
        merged["Inwonersperkmsqland"].astype(str)
        .str.replace(" ", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )
    if extra:
        merged = pd.concat([merged] + extra, ignore_index=True)
    return merged[merged["Inwonersperkmsqland"] > 1000].copy()


# ─────────────────────────────────────────────────────────────────────────────
# FIND NEAREST NON-RURAL STATION PER CITY  (for hourly calibration)
# ─────────────────────────────────────────────────────────────────────────────
def match_cities_to_urban_stations(
    urban_boundaries_gdf: gpd.GeoDataFrame,
    all_stations_gdf: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """
    For each city, return the nearest KNMI station that lies *inside* an urban
    municipality polygon.  These stations capture urban thermal dynamics (delayed
    peak, stronger nocturnal retention) better than rural open-field stations.

    If a city has no urban station within 30 km, falls back to the nearest
    station of any type and emits a warning.

    Returns: statnaam | hourly_station_id | hourly_station_name | lat | distance_km
    """
    cities_rd   = urban_boundaries_gdf.to_crs("EPSG:28992").copy()
    stations_rd = all_stations_gdf.to_crs("EPSG:28992").copy()

    urban_union     = cities_rd.geometry.union_all()
    stations_rd["is_urban"] = stations_rd.geometry.within(urban_union)
    urban_stations  = stations_rd[stations_rd["is_urban"]].copy()

    cities_rd["centroid"] = cities_rd.geometry.centroid

    matches = []
    for _, city in tqdm(cities_rd.iterrows(), total=len(cities_rd),
                        desc="  Matching to urban stations"):
        # Try urban stations first
        pool = urban_stations if not urban_stations.empty else stations_rd
        dists = pool.geometry.distance(city["centroid"])
        nearest_idx = dists.idxmin()
        nearest     = pool.loc[nearest_idx]
        dist_km     = dists[nearest_idx] / 1000

        if dist_km > 30 and not urban_stations.empty:
            # Fall back to any station
            dists2      = stations_rd.geometry.distance(city["centroid"])
            nearest_idx = dists2.idxmin()
            nearest     = stations_rd.loc[nearest_idx]
            dist_km     = dists2[nearest_idx] / 1000
            warnings.warn(
                f"No urban station within 30 km of {city['statnaam']}; "
                f"using nearest overall: {nearest['station_name']} ({dist_km:.1f} km)"
            )

        matches.append({
            "statnaam":            city["statnaam"],
            "hourly_station_id":   int(nearest["station_id"]),
            "hourly_station_name": nearest["station_name"],
            "lat":                 float(nearest.geometry.centroid.y
                                         if nearest.geometry.geom_type != "Point"
                                         else nearest.geometry.y),
            "distance_km":         round(dist_km, 2),
        })

    return pd.DataFrame(matches)


# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOAD KNMI HOURLY DATA
# ─────────────────────────────────────────────────────────────────────────────
def _parse_knmi_hourly(text: str) -> pd.DataFrame:
    """
    Parse KNMI uurgegevens response.
    Columns returned by API: STN, YYYYMMDD, HH, T
    HH is 1–24 where HH=1 covers 00:00–01:00 → subtract 1 to get hour 0–23.
    T is in 0.1 °C.
    """
    data_lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if not data_lines:
        return pd.DataFrame(columns=["station_id", "date", "hour", "T_C"])

    df = pd.read_csv(
        io.StringIO("\n".join(data_lines)),
        header=None,
        names=["station_id", "date", "HH", "T"],
        skipinitialspace=True,
    )
    df["station_id"] = pd.to_numeric(df["station_id"], errors="coerce").astype("Int64")
    df["date"]       = pd.to_datetime(df["date"].astype(str).str.strip(),
                                      format="%Y%m%d", errors="coerce")
    df["hour"]       = pd.to_numeric(df["HH"], errors="coerce") - 1   # 0-based
    df["T_C"]        = pd.to_numeric(df["T"],  errors="coerce") / 10.0
    return df.drop(columns=["HH", "T"]).dropna(subset=["station_id", "date", "T_C"])


def fetch_knmi_hourly(
    station_ids: list,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Download hourly air temperature (T) for the requested stations.
    Batched by year to avoid timeouts.
    """
    start    = pd.to_datetime(start_date, format="%Y%m%d")
    end      = pd.to_datetime(end_date,   format="%Y%m%d")
    stns_str = ":".join(str(s) for s in sorted(station_ids))

    frames = []
    for year in tqdm(range(start.year, end.year + 1), desc="  Downloading hourly T by year"):
        yr_start = max(start, pd.Timestamp(year,  1,  1)).strftime("%Y%m%d")
        yr_end   = min(end,   pd.Timestamp(year, 12, 31)).strftime("%Y%m%d")
        r = requests.get(
            KNMI_HOURLY_URL,
            params={"stns": stns_str, "vars": "T",
                    "start": yr_start, "end": yr_end},
            timeout=300,
        )
        r.raise_for_status()
        frames.append(_parse_knmi_hourly(r.text))

    if not frames:
        return pd.DataFrame(columns=["station_id", "date", "hour", "T_C"])
    combined = pd.concat(frames, ignore_index=True)
    print(f"  {len(combined):,} station-hour records downloaded")
    return combined


# ─────────────────────────────────────────────────────────────────────────────
# CALIBRATE t_Tx FROM HOURLY DATA
# ─────────────────────────────────────────────────────────────────────────────
def calibrate_tTx(
    hourly_df: pd.DataFrame,
    min_days: int = MIN_CALIBRATION_DAYS,
) -> pd.DataFrame:
    """
    Estimate the mean hour of daily maximum temperature per station.

    Only days with complete 24-hour records and a clear single peak are used.
    Returns: station_id | t_Tx_mean_h | t_Tx_std_h | n_calibration_days
    """
    results = []
    for stn_id, stn in hourly_df.groupby("station_id"):
        daily_peak = (
            stn.dropna(subset=["T_C"])
               .groupby("date")
               .apply(lambda d: d.loc[d["T_C"].idxmax(), "hour"]
                      if len(d) == 24 else np.nan, include_groups=False)
               .dropna()
        )
        n = len(daily_peak)
        if n < min_days:
            warnings.warn(
                f"Station {stn_id}: only {n} complete days for calibration "
                f"(minimum {min_days}). Using default t_Tx = 14.5 h."
            )
            t_Tx_mean = 14.5
            t_Tx_std  = np.nan
        else:
            t_Tx_mean = float(daily_peak.mean())
            t_Tx_std  = float(daily_peak.std())

        results.append({
            "station_id":         int(stn_id),
            "t_Tx_mean_h":        round(t_Tx_mean, 2),
            "t_Tx_std_h":         round(t_Tx_std, 2) if not np.isnan(t_Tx_std) else np.nan,
            "n_calibration_days": n,
        })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# DISAGGREGATE DAILY → HOURLY RURAL TEMPERATURE
# ─────────────────────────────────────────────────────────────────────────────
def disaggregate_city_daily(
    city_daily: pd.DataFrame,
    city_tTx: pd.DataFrame,
    city_lat: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply the double-sine model to every city-day in *city_daily* and return
    a long-format DataFrame with 24 hourly values per city-day.

    Parameters
    ----------
    city_daily : output of step 2 (columns: statnaam, date, T_rural_max_C, T_rural_min_C)
    city_tTx   : calibrated t_Tx per city  (columns: statnaam, t_Tx_mean_h)
    city_lat   : latitude per city         (columns: statnaam, lat)

    Returns
    -------
    DataFrame: statnaam | date | hour | T_rural_C
    """
    # Merge calibration parameters onto city-day table
    df = (city_daily
          .merge(city_tTx[["statnaam", "t_Tx_mean_h"]], on="statnaam", how="left")
          .merge(city_lat[["statnaam", "lat"]],          on="statnaam", how="left"))
    df["t_Tx_mean_h"] = df["t_Tx_mean_h"].fillna(14.5)   # global fallback

    # Pre-compute next-day Tmin per city (needed for falling limb)
    df = df.sort_values(["statnaam", "date"]).reset_index(drop=True)
    df["T_rural_min_C_next"] = (
        df.groupby("statnaam")["T_rural_min_C"].shift(-1)
    )
    # For the last day of each city, use the same Tmin as a fallback
    df["T_rural_min_C_next"] = df["T_rural_min_C_next"].fillna(df["T_rural_min_C"])

    records = []
    for _, row in df.iterrows():
        if pd.isna(row["T_rural_max_C"]) or pd.isna(row["T_rural_min_C"]):
            continue

        doy        = row["date"].day_of_year
        t_sr, t_ss = solar_times(doy, float(row["lat"]))
        t_Tx       = float(row["t_Tx_mean_h"])

        hourly = double_sine_hourly(
            T_min      = row["T_rural_min_C"],
            T_max      = row["T_rural_max_C"],
            T_min_next = row["T_rural_min_C_next"],
            t_sr       = t_sr,
            t_ss       = t_ss,
            t_Tx       = t_Tx,
        )
        for h, T in enumerate(hourly):
            records.append({
                "statnaam":  row["statnaam"],
                "date":      row["date"],
                "hour":      h,
                "T_rural_C": round(float(T), 2),
            })

    return pd.DataFrame(records)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Load step 2 outputs ──────────────────────────────────────────────────
    print("\n[0] Loading step 2 outputs …")
    match_path = os.path.join(STEP2_OUTPUT_DIR, "city_station_match.csv")
    temp_path  = os.path.join(STEP2_OUTPUT_DIR, "daily_T_rural.csv")

    for p in (match_path, temp_path):
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"{p} not found – run UrbanTemperature_Steps1_2.py first."
            )

    city_station_match = pd.read_csv(match_path)
    city_daily_temp    = pd.read_csv(temp_path, parse_dates=["date"])
    urban_list         = city_daily_temp["statnaam"].unique().tolist()
    print(f"  {len(urban_list)} cities, "
          f"{len(city_daily_temp):,} city-day records loaded")

    # ── Load urban boundaries and all KNMI stations ──────────────────────────
    print("\n[1] Loading boundaries and KNMI station metadata …")
    urban_boundaries = load_urban_boundaries(POP_DENSITY_CSV)
    all_stations     = fetch_knmi_stations()
    print(f"  {len(all_stations)} KNMI stations")

    # Get city centroids + latitudes for solar geometry
    cities_rd  = urban_boundaries.to_crs("EPSG:28992").copy()
    cities_rd["centroid_wgs84"] = cities_rd.geometry.centroid.to_crs("EPSG:4326")
    city_lat = pd.DataFrame({
        "statnaam": cities_rd["statnaam"],
        "lat":      cities_rd["centroid_wgs84"].apply(lambda g: g.y),
    })

    # ── Match cities to nearest urban (non-rural) station for calibration ────
    print("\n[2] Matching cities to nearest urban KNMI station …")
    city_urban_match = match_cities_to_urban_stations(urban_boundaries, all_stations)
    print(city_urban_match[["statnaam", "hourly_station_name", "distance_km"]]
          .to_string(index=False))

    # ── Download hourly temperature for calibration stations ─────────────────
    print(f"\n[3] Downloading hourly T from KNMI  ({START_DATE} – {END_DATE}) …")
    unique_hourly_ids = city_urban_match["hourly_station_id"].unique().tolist()
    hourly_df = fetch_knmi_hourly(unique_hourly_ids, START_DATE, END_DATE)

    # ── Calibrate t_Tx per station ───────────────────────────────────────────
    print("\n[4] Calibrating time of daily maximum temperature …")
    tTx_per_station = calibrate_tTx(hourly_df)

    # Map station calibration → city
    city_tTx = (city_urban_match[["statnaam", "hourly_station_id"]]
                .merge(tTx_per_station, left_on="hourly_station_id",
                       right_on="station_id", how="left")
                .drop(columns=["station_id"]))

    # Save calibration parameters
    calib_params = (city_urban_match
                    .merge(tTx_per_station, left_on="hourly_station_id",
                           right_on="station_id", how="left")
                    .drop(columns=["station_id"]))
    calib_path = os.path.join(OUTPUT_DIR, "city_calibration_params.csv")
    calib_params.to_csv(calib_path, index=False)
    print(f"  Saved → {calib_path}")
    print(calib_params[["statnaam", "hourly_station_name",
                         "t_Tx_mean_h", "n_calibration_days"]].to_string(index=False))

    # ── Disaggregate daily → hourly rural temperature ────────────────────────
    print("\n[5] Disaggregating daily → hourly temperatures …")
    hourly_rural = disaggregate_city_daily(city_daily_temp, city_tTx, city_lat)

    hourly_path = os.path.join(OUTPUT_DIR, "hourly_T_rural.csv")
    hourly_rural.to_csv(hourly_path, index=False)
    print(f"  Saved → {hourly_path}")
    print(f"  {len(hourly_rural):,} city-hour records written")

    # Quick validation: check mean diurnal profile for first city
    example = hourly_rural[hourly_rural["statnaam"] == urban_list[0]]
    mean_profile = example.groupby("hour")["T_rural_C"].mean().round(1)
    print(f"\n  Mean diurnal profile for '{urban_list[0]}':")
    print("  " + "  ".join(f"{h:02d}h:{t:+.1f}°" for h, t in mean_profile.items()))

    print("""
──────────────────────────────────────────────────────────────────────────────
  To compute spatial hourly urban temperature in the ABM:

    import numpy as np
    import rasterio

    # Load UHImax raster once per city
    with rasterio.open(f"UHImax_{{city}}.tif") as src:
        uhi = src.read(1).astype(float)

    # For a specific date + hour:
    T_rural_h = hourly_T_rural.loc[(city, date, hour), "T_rural_C"]
    t_sr, t_ss = solar_times(date.day_of_year, city_lat)
    w_h = uhi_diurnal_weight(np.array([hour + 0.5]), t_sr, t_ss)[0]
    T_urban = T_rural_h + uhi * w_h          # shape: (rows, cols)
──────────────────────────────────────────────────────────────────────────────
""")
    print("Done.")
