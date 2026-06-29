---
name: spatial
description: >-
  Handles and analyzes spatial / geographic data in R: loads vector data (sf),
  raster/gridded data (terra / stars), sets or transforms the CRS explicitly,
  performs spatial joins with the correct predicate, distinguishes areal
  (polygon) from point-event data, tests spatial autocorrelation (Moran's I via
  spdep), warns about the modifiable areal unit problem (MAUP) and the
  ecological fallacy, applies smoothing / shrinkage for small-area rates, and
  produces choropleth or point maps. Use when the user says: spatial data, GIS,
  shapefile, geojson, CRS, coordinate reference system, lat/long, lat/lng,
  longitude, latitude, spatial join, spatial autocorrelation, Moran's I,
  choropleth, areal data, polygon data, point data with coordinates, distance or
  area calculation, or map visualization. NOT for non-spatial analysis even if
  the dataset happens to contain a region column with no geometry attached.
---

# /datavidence-healthanalysis:spatial

> Operationalizes the spatial module rules in `template/docs/analysis/modules/spatial.md`
> (factory) and any child-level spatial policy in `.claude/policies/analysis/`.
> Apply `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION) throughout. Output artifacts follow `../_shared/spec-artifact.md`
> when a sizeable spec is emitted.

## When to use / when NOT to use

- **Use it when:** the task involves geometry objects, coordinate data, shapefiles,
  GeoJSON, rasters, distance/area computation, spatial joins, spatial autocorrelation,
  or map visualisation.
- **Do NOT use it when:** the data has a region label or admin-unit name but NO
  geometry is loaded or linked -- that is a categorical join, not a spatial operation.
  Also not for non-spatial statistical analysis of region-aggregated numbers
  (use specify-regression or frame-study instead).

## What it does: the spatial workflow (in order)

1. **Load and inspect geometry.**
   Read vector data with `sf::st_read()`; raster / gridded data with
   `terra::rast()` or `stars::read_stars()`. Print the object class,
   layer name, geometry type, bbox, and CRS immediately after loading.
   Never assume data is valid: run `sf::st_is_valid()` and repair with
   `sf::st_make_valid()` when any feature is invalid.

2. **Set or verify the CRS explicitly -- no silent assumptions.**
   - If the source has a declared CRS (`sf::st_crs()` returns non-NA), record it.
   - If the CRS is missing or wrong, do NOT proceed: return
     `PENDING_LOCAL_DECISION -- CRS unknown; provide EPSG code or proj string`
     and stop.
   - For distance or area calculations, transform to a projected CRS appropriate
     for the study region (`sf::st_transform(crs = <EPSG>)`). Never compute
     distances in degrees.
   - Record the CRS (EPSG + name) in all output file headers and in the
     variable catalog entry for the geometry column.

3. **Classify data type and flag design implications.**
   - **Areal / polygon (admin units, census tracts, health-service areas):**
     flag MAUP risk -- results can change when boundaries change; document the
     chosen zoning scheme and its rationale. Flag ecological fallacy risk:
     area-level associations may not hold at the individual level; note the
     inference scope in the output.
   - **Point events (cases, facilities, addresses):**
     confirm that coordinates represent the correct geographic entity (residence,
     facility, birth address) and check for jitter / aggregation applied for
     privacy (`analysis/data-protection.md`).
   - **Raster / gridded exposure:** note spatial resolution, temporal coverage,
     and the alignment method used before linking to vector units.

4. **Spatial join.**
   Use `sf::st_join(x, y, join = sf::<predicate>)`. Select the predicate
   explicitly (default `st_intersects` is rarely the only correct choice):
   - `st_within` -- point-in-polygon membership.
   - `st_intersects` -- any overlap (default; use consciously).
   - `st_nearest_feature` -- nearest-neighbor assignment (requires distance CRS).
   After the join, count unmatched features (`sum(is.na(...))`) and report;
   flag as `PENDING_LOCAL_DECISION` if unmatched rate exceeds a threshold not
   set by the child protocol.

5. **Spatial autocorrelation check (areal data).**
   Before treating spatial units as independent observations, run Moran's I
   (`spdep::moran.test()`). Clarify the target of the test:
   - On the **raw outcome** (before fitting any model): tests marginal / pre-model
     spatial structure -- answers "is there spatial clustering in the outcome itself?"
   - On **model residuals** (after fitting a non-spatial model): tests residual
     autocorrelation -- answers "does the model leave spatial structure unexplained?"
   Both are valid; they address different questions and must not be conflated.
   State which target is used and why in the plan.
   - Build a neighbor structure with `spdep::poly2nb()` (queen contiguity default;
     document the choice) and convert to weights with `spdep::nb2listw()`.
   - Report Moran's I, expected value, p-value, and interpretation.
   - If Moran's I is significant: the independence assumption is violated --
     flag it and propose a spatial model (spatial lag, spatial error, or
     geographically weighted regression) as `PENDING_LOCAL_DECISION` unless
     already specified by the child SAP.
   - Neighbor-structure choice (queen vs rook, k-nearest, distance band) is a
     methodological decision: return `PENDING_LOCAL_DECISION` if not specified.

6. **Small-area rate smoothing.**
   When denominators are small (< ~20 per unit is a common heuristic, but defer
   to child protocol), raw rates are unstable. Apply empirical Bayes smoothing
   (`spdep::EBest()` for global, `spdep::EBlocal()` for local) or a
   Besag-York-Mollie (BYM) model (implement via `R-INLA` or `CARBayes`). Return
   `PENDING_LOCAL_DECISION -- smoothing method not pre-specified` if the child
   SAP is silent.

7. **Visualization.**
   Produce choropleths with `ggplot2 + geom_sf()` or `tmap`. Always include:
   - CRS note in the caption.
   - North arrow and scale bar (`ggspatial::annotation_north_arrow()` /
     `annotation_scale()`).
   - Color scale appropriate for data type (sequential for rates; diverging for
     differences; avoid rainbow). Note color-blind safety.
   - For point maps with many events, consider kernel density or hexbin to
     avoid overplotting.

8. **Geometry size guard.**
   Large geometries slow analysis. Apply `sf::st_simplify(preserveTopology = TRUE,
   dTolerance = <m>)` for display only (never simplify the analytic object).
   For rasters, confirm resolution is appropriate for the analysis scale.

9. **Data-protection check.**
   Before exporting or uploading: precise coordinates of individuals may be
   disclosive. Apply jitter or aggregation per `analysis/data-protection.md`.
   Do NOT export precise patient-level coordinates to non-restricted storage.

10. **Human sign-off gate.**
    Present: CRS chosen, data type classification (areal/point/raster),
    neighbor structure, Moran's I result, smoothing decision (if areal), and
    any open `PENDING_LOCAL_DECISION` items. Await explicit confirmation before
    proceeding to spatial modelling or final output. Silence is not consent.

## Pairs with (repo policy)

- `template/docs/analysis/modules/spatial.md` -- the module activation rule and
  package list (`sf`, `terra`, `stars`).
- `analysis/data-protection.md` (child) -- coordinate jitter / aggregation rule.
- `analysis/regenerables.md` + `analysis/data-onboarding.md` (child) -- large
  geometries are regenerable; connect, do not import raw binaries.
- `analysis/numeric-computation.md` (child) -- all numeric spatial calculations
  (areas, distances, rates) go to R, not mental arithmetic.

## Rules / invariants

- **CRS must be explicit.** Never assume WGS84 or any other CRS. Always read and
  record it; always transform before distance/area work.
- **Math by tool.** Moran's I, areas, distances, smoothed rates: delegate to R
  (`spdep`, `sf`, `terra`). No mental computation.
- **PENDING_LOCAL_DECISION, never a silent default.** Unresolved choices -- CRS,
  predicate, neighbor structure, smoothing method -- are stop-signals, not defaults.
- **MAUP and ecological fallacy warnings are mandatory** for areal data, not optional.
- **Data-protection check before any export** of individual-level coordinates.
- **Claim to evidence.** Every layer source, CRS, and join predicate anchors to
  reproducible code output or a project metadata file.

## Output

- **Inline (simple task):** reproducible R code block + printed summary (CRS, bbox,
  geometry type, join counts, Moran's I result). No separate artifact file needed.
- **Spatial analysis plan (sizeable):** a spec artifact per `../_shared/spec-artifact.md`:
  one `spatial-plan.md` (small) or a split `analysis/spatial/<name>/` directory
  (large) with a README router and `build/pending-decisions.md` listing all open
  `PENDING_LOCAL_DECISION` items.
- Open `PENDING_LOCAL_DECISION` items are always surfaced to the user before any
  spatial model or final map is produced.
