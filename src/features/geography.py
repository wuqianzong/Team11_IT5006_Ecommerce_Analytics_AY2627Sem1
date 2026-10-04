"""Geography lookup: IBGE boundary reference + polygon-filtered ZIP/state medians.

Implements feature_contract.md v1.2 §4 "Geography lookup: required algorithm",
"Boundary reference and provenance", and "Haversine and audit outputs".

The only transactional inputs are ``data/preprocessed/*.csv``. The single external
reference is the pinned IBGE ``BR_Pais_2024`` country polygon staged under
``docs/references/geography/`` (a documented, label-independent quality-control
exception).
"""
from __future__ import annotations

import json
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import contains_xy, covers, points

from src.common.loaders import sha256_file

from .contract import UNKNOWN, VALID_STATES, normalize_state

EARTH_RADIUS_KM = 6371.0

# Boundary edition identifier recorded in zip_centroids.csv and the reports.
BOUNDARY_VERSION = "BR_Pais_2024"

# Pinned archive SHA-256 for the IBGE BR_Pais_2024.zip reference. This is the
# expected value the supplied archive is verified against on every build; it is
# not a substitute for hashing the actual file (feature_contract.md §4).
_ARCHIVE_SHA256 = "e84c4d4ab199e646b5a180e0f5b7a991fe4c3d424dff8ae3dcf4495992c128d5"

# Members required to read the shapefile directly from the verified archive.
_ARCHIVE_MEMBERS = ("BR_Pais_2024.shp", "BR_Pais_2024.shx", "BR_Pais_2024.dbf",
                    "BR_Pais_2024.prj")

_TARGET_CRS_EPSG = 4326


def geography_dir(repo_root: Path) -> Path:
    return Path(repo_root) / "docs" / "references" / "geography"


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
        if not s.isdigit() or len(s) > 5:
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
    """Boundary-inclusive point-in-polygon (x=lng, y=lat).

    feature_contract.md §4 requires boundary-inclusive coverage. Shapely's
    vectorized ``covers`` does not use a prepared geometry, so it is O(parts)
    per point (≈13 minutes for the full geolocation table). ``contains_xy``
    uses GEOS's prepared-geometry XY path and is O(1) per point, but is strictly
    interior. Combining both is exactly boundary-inclusive and fast:

      * ``contains_xy`` marks every strictly-interior point in one vectorized pass;
      * exact ``covers`` is then run only on the (tiny) non-interior set, recovering
        points lying exactly on the boundary line.

    The result is identical to ``covers(polygon, points(lng, lat))`` for every
    point, with the fast path used for the interior majority.
    """
    lng = np.asarray(lng, dtype=float)
    lat = np.asarray(lat, dtype=float)
    inside = contains_xy(polygon, lng, lat)
    outside = np.nonzero(~inside)[0]
    if outside.size:
        inside[outside] = covers(polygon, points(lng[outside], lat[outside]))
    return inside


def _validate_geometry(geom):
    """Nonempty + valid boundary geometry; invalid geometry is rejected, never repaired.

    feature_contract.md §4: the initial policy has zero buffer, and any repair must
    be an explicit, documented, label-independent decision — not a silent
    ``buffer(0)`` applied by the builder.
    """
    if geom is None or geom.is_empty:
        raise ValueError("IBGE boundary dissolved to empty geometry.")
    if not geom.is_valid:
        raise ValueError(
            "IBGE boundary geometry is invalid; refusing to auto-repair "
            "(feature_contract.md §4 zero-buffer policy). Re-stage the pinned archive "
            "or document an explicit repair.")
    return geom


def _read_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Missing {manifest_path}; re-stage the boundary reference "
            f"(feature_contract.md §4).")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _build_boundary(archive: Path, gj: Path, manifest_path: Path, archive_sha: str):
    """Build the derived EPSG:4326 geometry and provenance manifest once.

    The shapefile is read directly from the archive whose SHA-256 was just
    verified, so the derived geometry is provably from the pinned ZIP rather than
    from a separately extracted copy that may have drifted. Expected members are
    checked before extraction (feature_contract.md §4).
    """
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        missing = [m for m in _ARCHIVE_MEMBERS if m not in names]
        if missing:
            raise ValueError(
                f"IBGE archive missing expected members {missing}; re-stage the "
                f"pinned archive (feature_contract.md §4).")
        with tempfile.TemporaryDirectory() as tmp:
            zf.extractall(tmp)
            gdf = gpd.read_file(Path(tmp) / "BR_Pais_2024.shp")

    if gdf.crs is None:
        raise ValueError("IBGE shapefile has no declared CRS (feature_contract.md §4).")
    src_crs = str(gdf.crs)
    gdf = gdf.to_crs("EPSG:4326")
    gdf = gdf.dissolve()  # union all country parts; dissolve retains supplied islands
    geom = _validate_geometry(gdf.geometry.iloc[0])

    out = gpd.GeoDataFrame({"geometry": [geom]}, crs="EPSG:4326")
    out.to_file(gj, driver="GeoJSON")

    manifest = {
        "source_url": (
            "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
            "malhas_municipais/municipio_2024/Brasil/BR_Pais_2024.zip"
        ),
        "product": "BR_Pais_2024 (IBGE national boundary)",
        "product_year": 2024,
        "boundary_version": BOUNDARY_VERSION,
        "retrieved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "archive_sha256": archive_sha,
        "archive_members_verified": list(_ARCHIVE_MEMBERS),
        "original_crs": src_crs,
        "target_crs": "EPSG:4326",
        "geometry_selection_rule": "union all country parts; retain supplied islands",
        "transformation": (
            "read shapefile members directly from the verified archive; "
            "to_crs EPSG:4326; dissolve to single geometry"),
        "repair": "none (invalid geometry rejected; zero-buffer policy)",
        "library_versions": {
            "geopandas": gpd.__version__,
            "shapely": __import__("shapely").__version__,
            "pyproj": __import__("pyproj").__version__,
        },
        "derived_geometry_file": gj.name,
        "derived_geometry_sha256": sha256_file(gj),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
    return geom, manifest


def prepare_boundary(repo_root: Path):
    """Load the EPSG:4326 country polygon, verifying provenance on every call.

    Always hashes the supplied archive against the pinned expected value. On a
    cached-geometry path, also verifies the derived geometry hash, declared CRS
    and geometry validity against the manifest. Returns ``(polygon, manifest)``.
    """
    gdir = geography_dir(repo_root)
    archive = gdir / "BR_Pais_2024.zip"
    gj = gdir / "BR_Pais_2024_4326.geojson"
    manifest_path = gdir / "boundary_manifest.json"

    if not archive.exists():
        raise FileNotFoundError(
            f"Missing {archive}. Stage the pinned IBGE BR_Pais_2024 archive under "
            f"{gdir} before running (feature_contract.md §4 boundary reference).")

    actual_archive_sha = sha256_file(archive)
    if actual_archive_sha != _ARCHIVE_SHA256:
        raise ValueError(
            f"IBGE archive SHA-256 mismatch: expected {_ARCHIVE_SHA256}, got "
            f"{actual_archive_sha}. Re-stage the pinned archive; no bounding-box "
            f"fallback (feature_contract.md §4).")

    if gj.exists():
        manifest = _read_manifest(manifest_path)
        actual_gj_sha = sha256_file(gj)
        expected_gj_sha = manifest.get("derived_geometry_sha256")
        if expected_gj_sha is None or actual_gj_sha != expected_gj_sha:
            raise ValueError(
                "Derived boundary geometry SHA-256 does not match boundary_manifest.json; "
                "re-stage the boundary reference rather than silently rebuilding.")
        gdf = gpd.read_file(gj)
        if gdf.crs is None or gdf.crs.to_epsg() != _TARGET_CRS_EPSG:
            raise ValueError(
                f"Derived boundary CRS {gdf.crs} is not EPSG:{_TARGET_CRS_EPSG}.")
        geom = gdf.geometry.union_all()
        geom = _validate_geometry(geom)
        return geom, manifest

    return _build_boundary(archive, gj, manifest_path, actual_archive_sha)


def _classify_geolocation(geolocation: pd.DataFrame):
    """Normalize geolocation and assign first-failure reasons for contract steps 1-4.

    Steps 1-4 cover key/coordinate/range validity (before country filtering); the
    polygon step is applied separately in ``build_zip_centroids``. Returns
    ``(df, reason, lat, lng)`` where ``reason`` holds mutually exclusive
    first-failure labels (None = passed steps 1-4).
    """
    df = geolocation.copy()
    df["_zip"] = df["geolocation_zip_code_prefix"].map(normalize_zip)
    df["_state"] = df["geolocation_state"].astype(str).str.strip().str.upper()
    lat = pd.to_numeric(df["geolocation_lat"], errors="coerce")
    lng = pd.to_numeric(df["geolocation_lng"], errors="coerce")
    # Loaders keep coordinates as strings so malformed numeric text survives to
    # this point (never crashing the read); replace them with the coerced numeric
    # values here so downstream medians aggregate numbers, not strings.
    df["geolocation_lat"] = lat
    df["geolocation_lng"] = lng

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

    return df, reason, lat, lng


def build_zip_centroids(geolocation: pd.DataFrame, polygon,
                        boundary_version: str = BOUNDARY_VERSION):
    """8-step polygon-filtered ZIP/state median lookup (feature_contract.md §4).

    Returns ``(centroids, filter_report)`` where centroids has one row per valid
    (zip, state) key — including zero-survivor keys with null coordinates — and
    filter_report tallies mutually exclusive first-failure reasons plus the
    number of surviving rows after each step.
    """
    df, reason, lat, lng = _classify_geolocation(geolocation)

    # 5. country polygon (boundary-inclusive)
    candidates = reason.isna()
    if candidates.any():
        cx = lng[candidates].to_numpy(dtype=float)
        cy = lat[candidates].to_numpy(dtype=float)
        inside = _point_covers(polygon, cx, cy)
        outside = candidates.copy()
        outside[candidates] = ~inside
        reason[outside] = "outside_polygon"

    vc = reason.value_counts(dropna=False).to_dict()
    total = int(len(reason))
    n_key = int(vc.get("invalid_key", 0))
    n_coord = int(vc.get("invalid_coords", 0))
    n_lat = int(vc.get("lat_out_of_range", 0))
    n_lng = int(vc.get("lng_out_of_range", 0))
    n_outside = int(vc.get("outside_polygon", 0))
    n_accepted = int(vc.get(None, 0))
    filter_report = {
        "total_rows": total,
        "accepted": n_accepted,
        "first_failure_reasons": {str(k): int(v) for k, v in vc.items()},
        "survivors_after_step": {
            "start": total,
            "after_invalid_key": total - n_key,
            "after_invalid_coords": total - n_key - n_coord,
            "after_lat_range": total - n_key - n_coord - n_lat,
            "after_lng_range": total - n_key - n_coord - n_lat - n_lng,
            "after_polygon": n_accepted,
        },
    }

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

    # 6. re-check median against the polygon; coordinate-wise medians can fall
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
    groups["boundary_version"] = boundary_version
    groups = groups.rename(columns={"_zip": "zip_prefix", "_state": "state"})
    groups = groups.sort_values(["zip_prefix", "state"]).reset_index(drop=True)
    groups = groups[["zip_prefix", "state", "accepted_count", "median_lat",
                     "median_lng", "resolution_status", "boundary_version"]]
    return groups, filter_report


def compute_geography_coverage(geolocation: pd.DataFrame, customers: pd.DataFrame,
                               sellers: pd.DataFrame, centroids: pd.DataFrame) -> dict:
    """Customer/seller lookup coverage before and after country filtering.

    A key is "globally valid" if it has at least one coordinate passing the
    key/coordinate/range steps (i.e. before polygon filtering). "after" means the
    key resolved to an in-polygon median. Uses the same valid-key denominator
    (feature_contract.md §4 "Haversine and audit outputs").
    """
    df, reason, _, _ = _classify_geolocation(geolocation)
    gv_keys = set(map(tuple, df.loc[reason.isna(), ["_zip", "_state"]]
                      .drop_duplicates().to_numpy()))
    resolved_keys = set(map(tuple, centroids.loc[
        centroids["resolution_status"] == "resolved",
        ["zip_prefix", "state"]].to_numpy()))

    def keys_of(table, zip_col, state_col):
        z = table[zip_col].map(normalize_zip)
        s = table[state_col].map(normalize_state)
        ok = z.notna() & (s != UNKNOWN)
        return set(map(tuple, pd.DataFrame({"z": z[ok], "s": s[ok]}).to_numpy()))

    def cov(keys):
        before = len(keys & gv_keys)
        after = len(keys & resolved_keys)
        return {
            "keys": len(keys),
            "before": before,
            "after": after,
            "coverage_after_over_before": (after / before) if before else None,
        }

    return {
        "customer": cov(keys_of(customers, "customer_zip_code_prefix", "customer_state")),
        "seller": cov(keys_of(sellers, "seller_zip_code_prefix", "seller_state")),
    }


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
