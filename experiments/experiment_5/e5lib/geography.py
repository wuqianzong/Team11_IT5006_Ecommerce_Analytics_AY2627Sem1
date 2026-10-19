"""ZIP centroids and order distances (s02 2.3, 2.5).

Provenance: copied from Milestone 2 `src/features/geography.py` (feature_contract v1.2 section 4):
ZIP normalisation, key and coordinate checks, boundary-inclusive IBGE polygon filter, ZIP/state
median centroids re-checked against the polygon, haversine distance over distinct sellers.
Changes for Experiment 5: the derived EPSG:4326 boundary is read with shapely alone (no
geopandas); the archive and derived-geometry hashes are verified against the staged manifest
and never rebuilt here; files are read through e5lib.data.reference so the run manifest
records them.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import shapely
from shapely import contains_xy, covers, points
from shapely.geometry import shape

from . import data
from .cleaning import BR_STATES, UNKNOWN, normalize_state
from .manifest import sha256

EARTH_RADIUS_KM = 6371.0
BOUNDARY_VERSION = "BR_Pais_2024"
ARCHIVE_SHA256 = "e84c4d4ab199e646b5a180e0f5b7a991fe4c3d424dff8ae3dcf4495992c128d5"


def load_boundary(stage: str = "s02_data"):
    """Verified IBGE country polygon (EPSG:4326) and its provenance."""
    archive = data.reference("geography/BR_Pais_2024.zip", stage)
    gj = data.reference("geography/BR_Pais_2024_4326.geojson", stage)
    manifest_path = data.reference("geography/boundary_manifest.json", stage)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    archive_sha, gj_sha = sha256(archive), sha256(gj)
    if archive_sha != ARCHIVE_SHA256 or manifest.get("archive_sha256") != ARCHIVE_SHA256:
        raise ValueError(f"IBGE archive sha256 {archive_sha} is not the pinned {ARCHIVE_SHA256}")
    if gj_sha != manifest.get("derived_geometry_sha256"):
        raise ValueError("derived boundary geometry does not match boundary_manifest.json; re-stage it")
    feats = json.loads(gj.read_text(encoding="utf-8"))["features"]
    geom = shapely.union_all([shape(f["geometry"]) for f in feats])
    if geom.is_empty or not geom.is_valid:
        raise ValueError("IBGE boundary geometry is empty or invalid; it is never repaired")
    shapely.prepare(geom)
    provenance = {"boundary_version": BOUNDARY_VERSION, "archive_sha256": archive_sha,
                  "derived_geometry_sha256": gj_sha, "original_crs": manifest.get("original_crs"),
                  "target_crs": manifest.get("target_crs"), "repair": manifest.get("repair"),
                  "shapely": shapely.__version__}
    return geom, provenance


def normalize_zip(value) -> str | None:
    """Zero-padded 5-digit ZIP prefix string, or None."""
    if value is None or value is pd.NA or (isinstance(value, float) and not np.isfinite(value)):
        return None
    s = str(value).strip()
    if not s.isdigit() or len(s) > 5:
        return None
    return f"{int(s):05d}"


def haversine_km(lat1, lon1, lat2, lon2) -> np.ndarray:
    lat1, lon1, lat2, lon2 = (np.radians(np.asarray(x, dtype=float)) for x in (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _covers(polygon, lng, lat) -> np.ndarray:
    """Boundary-inclusive point-in-polygon: fast interior test, exact covers() for the rest."""
    lng, lat = np.asarray(lng, dtype=float), np.asarray(lat, dtype=float)
    inside = contains_xy(polygon, lng, lat)
    rest = np.nonzero(~inside)[0]
    if rest.size:
        inside[rest] = covers(polygon, points(lng[rest], lat[rest]))
    return inside


def zip_centroids(geolocation: pd.DataFrame, polygon) -> tuple[pd.DataFrame, dict]:
    """Median lat/lng per (ZIP prefix, state) over in-country rows; one row per valid key."""
    df = geolocation.copy()
    df["_zip"] = df["geolocation_zip_code_prefix"].map(normalize_zip)
    df["_state"] = df["geolocation_state"].astype("string").str.strip().str.upper()
    lat, lng = df["geolocation_lat"].astype(float), df["geolocation_lng"].astype(float)
    reason = pd.Series(None, index=df.index, dtype=object)
    reason[df["_zip"].isna() | ~df["_state"].isin(BR_STATES)] = "invalid_key"
    reason[reason.isna() & (lat.isna() | lng.isna() | ~np.isfinite(lat) | ~np.isfinite(lng))] = "invalid_coords"
    reason[reason.isna() & ((lat < -90) | (lat > 90))] = "lat_out_of_range"
    reason[reason.isna() & ((lng < -180) | (lng > 180))] = "lng_out_of_range"
    cand = reason.isna()
    inside = _covers(polygon, lng[cand], lat[cand])
    out_idx = cand[cand].index[~inside]
    reason[out_idx] = "outside_polygon"

    valid = df[reason != "invalid_key"].assign(_ok=reason.isna().astype(int))
    groups = valid.groupby(["_zip", "_state"], sort=True).agg(accepted_count=("_ok", "sum")).reset_index()
    acc = valid[valid["_ok"] == 1]
    med = acc.groupby(["_zip", "_state"], sort=True).agg(
        median_lat=("geolocation_lat", "median"), median_lng=("geolocation_lng", "median")).reset_index()
    groups = groups.merge(med, on=["_zip", "_state"], how="left")
    has = groups["median_lat"].notna()
    ok = _covers(polygon, groups.loc[has, "median_lng"], groups.loc[has, "median_lat"])
    bad = groups.index[has][~ok]
    groups.loc[bad, ["median_lat", "median_lng"]] = np.nan
    groups["resolution_status"] = np.where(groups["accepted_count"] == 0, "no_surviving_coordinates",
                                           np.where(groups["median_lat"].isna(), "median_outside_polygon",
                                                    "resolved"))
    groups = groups.rename(columns={"_zip": "zip_prefix", "_state": "state"})
    counts = reason.value_counts(dropna=False)
    report = {"rows": int(len(df)), "accepted": int(reason.isna().sum()),
              "first_failure_reasons": {str(k): int(v) for k, v in counts.items() if k is not None and k == k},
              "keys": int(len(groups)),
              "keys_by_status": {k: int(v) for k, v in groups["resolution_status"].value_counts().items()}}
    return groups, report


def distance_features(orders, customers, sellers, order_seller_pairs, centroids) -> pd.DataFrame:
    """distance_km_max, distance_missing_fraction, interstate_share per order (distinct sellers).

    An unresolved customer coordinate makes every seller distance unresolved; any unresolved
    seller nulls distance_km_max (never a partial maximum).
    """
    cent = centroids[["zip_prefix", "state", "median_lat", "median_lng"]].rename(
        columns={"median_lat": "lat", "median_lng": "lng"})

    def locate(tbl, zip_col, state_col):
        t = tbl.assign(_zip=tbl[zip_col].map(normalize_zip), _state=tbl[state_col].map(normalize_state))
        return t.merge(cent, left_on=["_zip", "_state"], right_on=["zip_prefix", "state"], how="left")

    cust = locate(customers, "customer_zip_code_prefix", "customer_state")
    sell = locate(sellers, "seller_zip_code_prefix", "seller_state")
    osp = order_seller_pairs.drop_duplicates(["order_id", "seller_id"]).merge(
        sell[["seller_id", "_state", "lat", "lng"]].rename(
            columns={"_state": "seller_state", "lat": "s_lat", "lng": "s_lng"}), on="seller_id", how="left")
    osp = osp.merge(orders[["order_id", "customer_id"]], on="order_id", how="left").merge(
        cust[["customer_id", "_state", "lat", "lng"]].rename(
            columns={"_state": "cust_state", "lat": "c_lat", "lng": "c_lng"}), on="customer_id", how="left")
    osp["s_ok"] = osp["s_lat"].notna() & osp["s_lng"].notna()
    osp["c_ok"] = osp["c_lat"].notna() & osp["c_lng"].notna()
    osp["dist"] = haversine_km(osp["c_lat"], osp["c_lng"], osp["s_lat"], osp["s_lng"])
    osp["state_ok"] = (osp["cust_state"] != UNKNOWN) & (osp["seller_state"] != UNKNOWN) \
        & osp["cust_state"].notna() & osp["seller_state"].notna()
    osp["inter"] = osp["seller_state"] != osp["cust_state"]
    g = osp.groupby("order_id").agg(n=("seller_id", "size"), s_bad=("s_ok", lambda s: int((~s).sum())),
                                    c_ok=("c_ok", "first"), st_ok=("state_ok", "all"),
                                    inter=("inter", "sum"), dmax=("dist", "max"))
    unresolved = np.where(g["c_ok"].to_numpy(bool), g["s_bad"].to_numpy(int), g["n"].to_numpy(int))
    n = g["n"].to_numpy(int)
    return pd.DataFrame({
        "distance_km_max": np.where(unresolved == 0, g["dmax"].to_numpy(float), np.nan),
        "distance_missing_fraction": np.where(n > 0, unresolved / n, np.nan),
        "interstate_share": np.where(g["st_ok"].to_numpy(bool) & (n > 0), g["inter"].to_numpy(float) / n, np.nan),
    }, index=g.index)
