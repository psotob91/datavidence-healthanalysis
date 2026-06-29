---
name: big-data-triage
description: >-
  Picks the compute engine and memory pattern for large or slow datasets, then
  emits a concrete setup plan. Triggers when the user says: big data, on-disk,
  out of memory, slow query, millions of rows, dataset too large, speed up,
  data.table vs duckdb, parquet, arrow, chunked, memory pressure, or query
  taking too long. Scope is ENGINE SELECTION and computational pattern only --
  not the statistical method or estimand (those belong to the relevant analysis
  skills). Use it when the blocking problem is size, speed, or memory, not
  correctness of the analysis. Operationalizes the computational-efficiency
  policy.
---

# /datavidence-healthanalysis:big-data-triage

> Operationalizes `.claude/policies/analysis/computational-efficiency.md`. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION) and emit the plan per `../_shared/spec-artifact.md`
> (single focused document, no unnecessary render).

## Scope boundary

This skill decides the **engine** and **pattern** for large or slow data.
It does NOT touch:

- Statistical methods, estimands, or model choice -- those belong to the
  relevant analysis skill (e.g., `assess-missingness`, `validate-assumptions`).
- Parallelism worker counts or backend choice -- those are handled by the
  parallelism section of the computational-efficiency policy; this skill
  addresses size and query patterns.
- Data onboarding (connecting / copying raw data) -- that is `onboard-data`.

If the user asks "which model should I use on this large dataset?" answer the
engine question here and redirect the model question to the appropriate skill.

## When to use / when NOT to use

- **Use it when:** data does not fit in RAM, a query or load step is slow,
  the user is choosing between `data.table`, DuckDB, Arrow/Parquet, or chunked
  reads, or any phrasing signals that size or speed is the bottleneck.
- **Do NOT use it when:** the dataset is small and clearly in-memory (a few
  thousand rows, well under half RAM) and the question is purely about the
  analysis method -- skip directly to the relevant analysis skill.

## What it does (in order, no skipping)

### Step 1 -- Probe size and memory

Ask (or infer from context) before choosing an engine:

- **Row count and column count** of the dataset(s) involved.
- **File format:** CSV, Parquet, RDS, database, other.
- **Available RAM** on the analyst's machine. If unknown, emit
  `PENDING_LOCAL_DECISION: available-RAM` and use a conservative placeholder
  (4 GB) for the decision table below.
- **Whether the dataset must stay on disk** (size >> RAM, privacy/regulatory
  restriction, or network share).

Do not guess. Surface every unknown as `PENDING_LOCAL_DECISION: <what>`.

### Step 2 -- Choose engine

Apply the decision table from the policy:

| Situation | Engine |
|---|---|
| Data fits comfortably in RAM (< ~½ RAM rule-of-thumb) | `data.table` |
| Data lives on disk (Parquet/CSV), footprint would exceed ~½ RAM, or the query is join/aggregation-heavy | DuckDB (via `duckdb` R package) |
| Pipeline mixes both: DuckDB aggregates/filters → `data.table` models | Compose: DuckDB first, then `data.table` |
| Data is already Parquet and queries are projection/filter only | Arrow (`arrow` package) as lightweight alternative to DuckDB |

The ½-RAM threshold is a **rule of thumb, not a hard cutoff** -- profile first
if in doubt. Flag `PENDING_LOCAL_DECISION: RAM-threshold` if the analyst has
not confirmed available RAM.

### Step 3 -- Specify the pattern

Once the engine is chosen, state the concrete pattern:

**data.table path:**
- Replace row loops with vectorized `data.table` operations (`:=`, `[i, j, by]`).
- Use keys (`setkey`) for repeated joins or ordered access.
- Avoid `apply`-family loops over rows; delegate any iterative math to R
  vectorized functions or pre-aggregated `data.table` steps.

**DuckDB path:**
- Open an in-process DuckDB connection; read Parquet/CSV directly via
  `duckdb::duckdb_read_csv()` or `duckdb_register()` without loading into R first.
- Push filtering, aggregation, and joins DOWN into the DuckDB query layer before
  collecting into R (`collect()`).
- After collection the result set is small enough for `data.table` or `tibble`.

**Arrow path (Parquet, projection/filter only):**
- Use `arrow::open_dataset()` with `filter()` + `select()` + `collect()`.
- Do not pull unnecessary columns; Arrow pushes predicates to the file scanner.

**All paths -- cache expensive steps:**
- Wrap long-running steps in `{targets}`: intermediate results are cached and
  re-used on re-runs without re-executing the expensive step.
- Alternatively save intermediate outputs as `.qs` (via `qs` package) or `.fst`
  (via `fst`) for fast serialization and reload.
- Quarto `freeze: true` caches rendered chunks across sessions.

### Step 4 -- Profile before optimizing further

If the analyst has already written code and the problem is slowness (not size):

- Instruct profiling FIRST: `profvis::profvis({ ... })` or `system.time()` to
  locate the bottleneck before rewriting.
- Correctness before speed: confirm that the slow code is correct before
  replacing it with a vectorized equivalent.
- Do not recommend parallelism as the first fix. Vectorization (Step 3) and
  engine choice (Step 2) come before parallelism; recommend the
  computational-efficiency policy's parallelism section only after engine and
  vectorization are addressed. When parallelism is warranted: run
  `scripts/sysinfo.py` first to probe available cores and RAM before setting
  worker counts; use L'Ecuyer-CMRG streams (`RNGkind("L'Ecuyer-CMRG")` +
  `parallel::clusterSetRNGStream()`) for reproducible seeds across workers.

### Step 5 -- Emit the plan

Produce a focused plan document per `../_shared/spec-artifact.md`:

- **Engine chosen** and the one-line rationale (size, format, query type).
- **Pattern snippet** (pseudo-code or skeleton, not a full implementation) for
  the chosen path.
- **Cache/checkpoint plan** if the pipeline has steps expected to run > a few
  minutes.
- **PENDING_LOCAL_DECISION register** at the end: every open choice (RAM,
  threshold, file format, targets vs qs) that the analyst must confirm.

Do not write a full implementation until the engine and pattern are confirmed
by the analyst. A skeleton showing structure (not results) may be included to
illustrate the proposed approach.

## Rules / invariants

- **Profile before optimizing.** Identify the bottleneck before rewriting code.
- **Correctness before speed.** A fast wrong answer is worse than a slow right one.
- **Vectorize; no row loops.** Row-by-row iteration is a last resort, not a default.
- **Push work down.** Filtering and aggregation happen inside the engine (DuckDB
  query, Arrow predicate pushdown, `data.table` `[i, j, by]`) -- not in R loops
  after collection.
- **Cache long runs.** Any step expected to take > a few minutes gets a `{targets}`
  target or a checkpoint file; never re-run expensively what can be cached.
- **PENDING_LOCAL_DECISION, never silent defaults.** RAM, thresholds, and format
  choices not confirmed by the analyst are named PENDING, not guessed.
- **Math by tool.** Row counts, timing benchmarks, and memory estimates are
  produced by R code; do not compute or guess them in model output.

## Pairs with (repo policy)

- `.claude/policies/analysis/computational-efficiency.md` (the authoritative rule).
- **Prior-if:** `onboard-data` -- know the file format and location before
  choosing an engine.
- **Next-if speed still bottlenecked:** revisit the parallelism section of the
  computational-efficiency policy after engine and vectorization are in place.
- **Next-if analysis:** once the engine plan is confirmed, proceed to the relevant
  analysis skill (e.g., `run-ida`, `assess-missingness`, `validate-assumptions`).
