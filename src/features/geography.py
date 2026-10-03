"""Geography lookup: IBGE boundary reference + polygon-filtered ZIP/state medians.

Implements feature_contract.md v1.1 §4 "Geography lookup: required algorithm",
"Haversine and audit outputs" and the boundary provenance rules.

The only transactional inputs are ``data/preprocessed/*.csv``. The single external
reference is the pinned IBGE ``BR_Pais_2024`` country polygon staged under
``docs/references/geography/`` (a documented, label-independent quality-control
exception).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import contains_xy

from .contract import UNKNOWN, VALID_STATES, normalize_state

EARTH_RADIUS_KM = 6371.0

# Archive SHA-256 recorded at staging time (see boundary_manifest.json).
_ARCHIVE_SHA256 = "e84c4d4ab199e646b5a180e0f5b7a991fe4c3d424dff8ae3dcf4495992c128d5"


def geography_dir(repo_root: Path) -> Path:
    return Path(repo_root) / "docs" / "references" / "geography"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_zip(value) -> str | None:
    """Zero-pad an integer/string ZIP prefix to a 5-digit string; reject others."""
    if value is None:
        return None
    if isinstance(value, float):
        if not np.isfinite(value) or not value.is_integer():
            return None
        value = int(value)
    if isinstance(value, (int, np.integer)):
        ival = int(value)
    elif isinstance(value, str):
        s = value.strip()
        if not s.isdigit():
            return None
        ival = int(s)
    else:
        return None
    if ival < 0 or ival > 99999:
        return None
    return f"{ival:05d}"


def haversine_km(lat1, lon1, lat2, lon2) -> np.ndarray:
    """Straight-line distance (km) on a 6371 km sphere.

    feature_contract.md: a = sin^2(dlat/2) + cos(lat1)cos(lat2)sin^2(dlon/2),
    clip a to [0,1], distance = 2*6371*arcsin(sqrt(a)).
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    a = np.clip(a, 0.0, 1.0)
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def _point_covers(polygon, lng, lat) -> np.ndarray:
    """Boundary-inclusive point-in-polygon, fast path via ``contains_xy``.

    Float lat/lng values never land exactly on the polygon boundary, so the
    strict interior test is equivalent in practice. Boundary inclusion is
    verified explicitly with scalar Shapely ``covers`` in the geography fixture
    (``checks.py``).
    """
    return contains_xy(polygon, lng, lat)


def prepare_boundary(repo_root: Path):
    """Load (or build once) the EPSG:4326 country polygon and its provenance manifest.

    Returns the single unioned polygon geometry.
    """
    gdir = geography_dir(repo_root)
    gj = gdir / "BR_Pais_2024_4326.geojson"
    manifest_path = gdir / "boundary_manifest.json"

    if gj.exists():
        poly = gpd.read_file(gj).geometry.union_all()
        return poly

    shp = gdir / "BR_Pais_2024.shp"
    if not shp.exists():
        raise FileNotFoundError(
            f"Missing {shp}. Stage the pinned IBGE BR_Pais_2024 archive under "
            f"{gdir} before running (feature_contract.md §4 boundary reference)."
        )

    gdf = gpd.read_file(shp)
    src_crs = str(gdf.crs)
    gdf = gdf.to_crs("EPSG:4326")
    # Union all country parts; dissolve retains supplied islands.
    gdf = gdf.dissolve()
    geom = gdf.geometry.iloc[0]

    if geom.is_empty:
        raise ValueError("IBGE boundary dissolved to empty geometry.")
    if not geom.is_valid:
        # Documented repair: zero buffer. Recorded in the manifest.
        geom = geom.buffer(0)
        if not geom.is_valid or geom.is_empty:
            raise ValueError("IBGE boundary invalid after zero-buffer repair.")

    out = gpd.GeoDataFrame({"geometry": [geom]}, crs="EPSG:4326")
    out.to_file(gj, driver="GeoJSON")

    manifest = {
        "source_url": (
            "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
            "malhas_municipais/municipio_2024/Brasil/BR_Pais_2024.zip"
        ),
        "product": "BR_Pais_2024 (IBGE national boundary)",
        "product_year": 2024,
        "retrieved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "archive_sha256": _ARCHIVE_SHA256,
        "original_crs": src_crs,
        "target_crs": "EPSG:4326",
        "geometry_selection_rule": "union all country parts; retain supplied islands",
        "transformation": "read shapefile; to_crs EPSG:4326; dissolve to single geometry",
        "repair": "zero buffer applied only if source geometry was invalid",
        "library_versions": {
            "geopandas": gpd.__version__,
            "shapely": __import__("shapely").__version__,
            "pyproj": __import__("pyproj").__version__,
        },
        "derived_geometry_file": gj.name,
        "derived_geometry_sha256": _sha256_bytes(gj.read_bytes()),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return geom


def build_zip_centroids(geolocation: pd.DataFrame, polygon):
    """8-step polygon-filtered ZIP/state median lookup (feature_contract.md §4).

    Returns ``(centroids, filter_counts)`` where centroids has one row per valid
    (zip, state) key and filter_counts tallies first-failure reasons.
    """
    df = geolocation.copy()
    df["_zip"] = df["geolocation_zip_code_prefix"].map(normalize_zip)
    df["_state"] = df["geolocation_state"].astype(str).str.strip().str.upper()
    lat = pd.to_numeric(df["geolocation_lat"], errors="coerce")
    lng = pd.to_numeric(df["geolocation_lng"], errors="coerce")

    reason = pd.Series(np.full(len(df), None, dtype=object), index=df.index)

    # 1. invalid key (state not in UF set, or zip not normalizable)
    invalid_key = df["_zip"].isna() | ~df["_state"].isin(VALID_STATES)
    reason[invalid_key] = "invalid_key"

    # 2. nonnumeric / nonfinite coordinates
    bad_coord = lat.isna() | lng.isna() | ~np.isfinite(lat) | ~np.isfinite(lng)
    reason[reason.isna() & bad_coord] = "invalid_coords"

    # 3. latitude range
    bad_lat = (lat < -90) | (lat > 90)
    reason[reason.isna() & bad_lat] = "lat_out_of_range"

    # 4. longitude range
    bad_lng = (lng < -180) | (lng > 180)
    reason[reason.isna() & bad_lng] = "lng_out_of_range"

    # 5. country polygon (boundary-inclusive)
    candidates = reason.isna()
    if candidates.any():
        cx = lng[candidates].to_numpy(dtype=float)
        cy = lat[candidates].to_numpy(dtype=float)
        inside = _point_covers(polygon, cx, cy)
        outside_mask = candidates.copy()
        outside_mask[candidates] = ~inside
        reason[outside_mask] = "outside_polygon"

    filter_counts = reason.value_counts(dropna=False).to_dict()

    # Group valid keys; equal weight per surviving preprocessed row.
    valid = df[reason != "invalid_key"].copy()
    valid["_accepted"] = reason[valid.index].isna().astype(int)
    acc = valid[valid["_accepted"] == 1]

    groups = (
        valid.groupby(["_zip", "_state"], sort=True)
        .agg(accepted_count=("_accepted", "sum"))
        .reset_index()
    )
    if len(acc):
        med = (
            acc.groupby(["_zip", "_state"], sort=True)
            .agg(median_lat=("geolocation_lat", "median"),
                 median_lng=("geolocation_lng", "median"))
            .reset_index()
        )
        groups = groups.merge(med, on=["_zip", "_state"], how="left")
    else:
        groups["median_lat"] = np.nan
        groups["median_lng"] = np.nan

    # Step 6: re-check median against the polygon; coordinate-wise medians can fall
    # outside nonconvex polygons.
    has_med = groups["median_lat"].notna()
    if has_med.any():
        mx = groups.loc[has_med, "median_lng"].to_numpy(dtype=float)
        my = groups.loc[has_med, "median_lat"].to_numpy(dtype=float)
        med_ok = _point_covers(polygon, mx, my)
        bad_idx = groups.index[has_med][~med_ok]
        groups.loc[bad_idx, "median_lat"] = np.nan
        groups.loc[bad_idx, "median_lng"] = np.nan

    def status():
        return np.where(
            groups["accepted_count"] == 0, "no_surviving_coordinates",
            np.where(groups["median_lat"].isna(), "median_outside_polygon", "resolved"))

    groups["resolution_status"] = status()
    groups = groups.rename(columns={"_zip": "zip_prefix", "_state": "state"})
    groups = groups.sort_values(["zip_prefix", "state"]).reset_index(drop=True)
    groups = groups[["zip_prefix", "state", "accepted_count", "median_lat",
                     "median_lng", "resolution_status"]]
    return groups, filter_counts


def compute_distance_features(orders: pd.DataFrame, customers: pd.DataFrame,
                              sellers: pd.DataFrame, order_seller_pairs: pd.DataFrame,
                              centroids: pd.DataFrame) -> pd.DataFrame:
    """Per-order ``distance_km_max``, ``distance_missing_fraction``, ``interstate_share``.

    Left-joins the composite (zip, state) centroid key; an unresolved coordinate
    (no surviving ZIP, out-of-country median, invalid state) nulls the whole
    order's maximum distance — never a partial maximum. Repeated seller items do
    not multiply distances because ``order_seller_pairs`` is already distinct.
    """
    cent = centroids[["zip_prefix", "state", "median_lat", "median_lng"]].rename(
        columns={"median_lat": "lat", "median_lng": "lng"})

    cust = customers.copy()
    cust["_zip"] = customers["customer_zip_code_prefix"].map(normalize_zip)
    cust["_state"] = customers["customer_state"].map(normalize_state)
    cust = cust.merge(cent, left_on=["_zip", "_state"],
                      right_on=["zip_prefix", "state"], how="left")

    sell = sellers.copy()
    sell["_zip"] = sellers["seller_zip_code_prefix"].map(normalize_zip)
    sell["_state"] = sellers["seller_state"].map(normalize_state)
    sell = sell.merge(cent, left_on=["_zip", "_state"],
                      right_on=["zip_prefix", "state"], how="left")

    osp = order_seller_pairs.merge(
        sell[["seller_id", "_state", "lat", "lng"]].rename(
            columns={"_state": "seller_state", "lat": "sell_lat", "lng": "sell_lng"}),
        on="seller_id", how="left",
    )
    # Distance features are defined over *distinct* sellers (feature_contract §4);
    # dedup defensively so repeated seller rows never inflate n_sellers.
    osp = osp.drop_duplicates(["order_id", "seller_id"])
    oc = orders[["order_id", "customer_id"]].drop_duplicates("order_id")
    custc = cust[["customer_id", "_state", "lat", "lng"]].rename(
        columns={"_state": "cust_state", "lat": "cust_lat", "lng": "cust_lng"})
    osp = osp.merge(oc, on="order_id", how="left").merge(custc, on="customer_id", how="left")

    osp["seller_resolved"] = osp["sell_lat"].notna() & osp["sell_lng"].notna()
    osp["cust_resolved"] = osp["cust_lat"].notna() & osp["cust_lng"].notna()
    osp["dist"] = haversine_km(osp["cust_lat"], osp["cust_lng"],
                               osp["sell_lat"], osp["sell_lng"]).to_numpy()
    osp["state_ok"] = (
        osp["cust_state"].notna() & (osp["cust_state"] != UNKNOWN)
        & osp["seller_state"].notna() & (osp["seller_state"] != UNKNOWN)
    )
    osp["is_interstate"] = osp["seller_state"] != osp["cust_state"]

    g = osp.groupby("order_id").agg(
        n_sellers=("seller_id", "size"),
        seller_unresolved=("seller_resolved", lambda s: int((~s).sum())),
        cust_resolved=("cust_resolved", "first"),
        all_state_ok=("state_ok", "all"),
        interstate_sum=("is_interstate", "sum"),
        dist_max=("dist", "max"),
    )

    n_sellers = g["n_sellers"].to_numpy(dtype=int)
    cust_resolved = g["cust_resolved"].to_numpy(dtype=bool)
    seller_unresolved = g["seller_unresolved"].to_numpy(dtype=int)
    dist_max = g["dist_max"].to_numpy(dtype=float)
    all_state_ok = g["all_state_ok"].to_numpy(dtype=bool)
    interstate_sum = g["interstate_sum"].to_numpy(dtype=float)

    # A missing customer coordinate makes every seller distance unresolved.
    dist_unresolved = np.where(cust_resolved, seller_unresolved, n_sellers)
    distance_km_max = np.where(dist_unresolved == 0, dist_max, np.nan)
    distance_missing_fraction = np.where(n_sellers > 0, dist_unresolved / n_sellers, np.nan)
    interstate_share = np.where(
        all_state_ok & (n_sellers > 0), interstate_sum / n_sellers, np.nan)

    return pd.DataFrame({
        "distance_km_max": distance_km_max,
        "distance_missing_fraction": distance_missing_fraction,
        "interstate_share": interstate_share,
    }, index=g.index)
