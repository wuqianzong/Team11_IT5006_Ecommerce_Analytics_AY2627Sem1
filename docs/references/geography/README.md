# Geography boundary reference — staging instructions

The ML feature builder filters geolocation coordinates against the pinned IBGE
country polygon (`feature_contract.md` §4). The archive is **not** supplied by the
repository — only `boundary_manifest.json` (provenance) is committed; the raw
archive, extracted shapefile and derived GeoJSON are git-ignored (see `.gitignore`).

## Reproducible staging (no runtime downloads)

1. Download the pinned archive from the official IBGE directory:

   - https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/Brasil/BR_Pais_2024.zip

2. Verify the archive SHA-256 **before** using it (expected value):

   - `e84c4d4ab199e646b5a180e0f5b7a991fe4c3d424dff8ae3dcf4495992c128d5`

3. Keep the archive as-is; the builder reads `BR_Pais_2024.shp` (and `.shx`,
   `.dbf`, `.prj`) **directly from the verified ZIP** — no extraction step. It
   first checks that all expected members are present, then extracts to a
   temporary directory, so the derived geometry is provably from the pinned
   archive.

4. Run the builder once; it reads the declared CRS (EPSG:4674), transforms to
   EPSG:4326, unions all country parts (retaining supplied islands), writes
   `BR_Pais_2024_4326.geojson` and refreshes `boundary_manifest.json` with the
   derived geometry hash and the verified member list.

On every build — including cached-geometry paths — the builder hashes the actual
archive and derived geometry, checks the declared CRS and geometry validity, and
fails clearly on any mismatch. Invalid geometry is **rejected**, never repaired
(the zero-buffer policy; no bounding-box fallback, no silent rebuild).
