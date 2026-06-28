---
name: map-clinical-codes
description: >-
  Assembles and validates clinical code sets -- ICD-9, ICD-10 / CIE-10, SNOMED-CT, RxNorm,
  ATC, CPT/PCS, LOINC -- and runs the mandatory code-list integrity checklist before any
  downstream use. Use when the user asks to build a diagnosis code list, medication code list,
  procedure code list, lab code list, run a crosswalk (GEM, ICD-9 to ICD-10, ICD-10-CM),
  compute a comorbidity index, map to phecodes or phecode, map to OMOP concept sets, or
  validate a code set against a source vocabulary. Operationalizes health/code-mapping.md.
  NOT for turning a code set into a yes/no patient label (that is phenotype-gate); NOT for
  denominators, person-time, or incidence/prevalence rates (that is design-indicator).
---

# /datavidence-healthanalysis:map-clinical-codes

> Operationalizes `.claude/policies/health/code-mapping.md`. Apply `../_shared/health-principles.md`
> (math-by-tool, claim-to-evidence, PENDING_LOCAL_DECISION, no invention) and emit the artifact
> per `../_shared/spec-artifact.md` -- for a code set the output is ordinarily a single manifest
> plus a small render; split to an indexed directory only when the set is large or multi-vocabulary.

## When to use / when NOT to use

- Use it when: assembling ICD/SNOMED/RxNorm/ATC/CPT/LOINC code sets; validating a crosswalk
  (GEM, national adaptations); grouping codes with a comorbidity index, phecodes, or OMOP concept
  sets; cleaning raw code columns before any analysis step.
- Do NOT use it when: applying the code set to classify patients into a yes/no condition label --
  that starts phenotype-gate, which consumes a validated code set as its input. Do NOT use it for
  denominators, person-time, or rate computation -- that is design-indicator. The pipeline order is
  map-clinical-codes -> phenotype-gate -> design-indicator; stay in lane.

## What it does: the mapping procedure (in order, no skipping)

Run the Code-list / mapping integrity checklist in `docs/health/checklists.md`; any "no" or
"unknown" is a stop -- fix it or return `PENDING_LOCAL_DECISION`.

1. **Declare provenance.** State source + version + extraction date for every vocabulary
   referenced (e.g. "ICD-10-CM FY 2026; phecodeX v1.0; AHRQ Elixhauser 2026-06-28"). Never
   inline an unsourced code vector. Store the list in `metadata/` and reference it from the
   variable definition.
2. **Choose one grouping approach per variable.** Pick based on analytic goal:
   - Comorbidity index (Charlson/Elixhauser) -- for confounding or case-mix adjustment.
   - Phecodes / phecodeX (Wei Lab) -- for phenome-wide grouping of ICD.
   - OMOP concept sets (OHDSI Standardized Vocabularies) -- for multi-site harmonization.
   Using different systems for *different* variables is fine; defining one variable two ways, or
   switching systems mid-pipeline, breaks comparability. Return PENDING_LOCAL_DECISION if the
   choice has not been made in the local protocol/SAP.
3. **State crosswalk direction and quantify loss.** ICD-9<->ICD-10 GEM maps are not bijections.
   Declare direction; report unmapped % and one-to-many %; re-map at source level; do not chain
   lossy maps. These numbers belong in the manifest.
4. **Apply the cleaning sequence in this exact order:**
   a. Force character type (never numeric).
   b. Trim whitespace + uppercase.
   c. ICD-9: zero-pad to 5 characters where needed. ICD-10: NEVER zero-pad.
   d. Split WHO dagger/asterisk pairs (etiology/manifestation codes).
   e. Terminal-X handling -- ICD-10-CM only: the `X` in positions 4-6 is a structural placeholder
      for the 7th character (A=initial / D=subsequent / S=sequela). Preserve all characters and
      validate against the official tabular list; do not strip from the right. WHO-ICD-10 admin
      placeholder X (some national extracts) may be dropped -- document which applies.
   f. Cascade-truncate to the 3-character header ONLY when a full-code match fails; log every
      truncation in the transformation log.
5. **Run validation gates.** Compute and report:
   - % orphan (code present in data but absent from vocabulary).
   - % unspecified (codes ending `.9` or equivalent).
   - % truncated (codes kept only at the 3-char header level).
   Compare against WARN/FAIL thresholds defined in `analysis/data-contracts.md`. Block the
   pipeline on FAIL; emit a structured warning on WARN. Return PENDING_LOCAL_DECISION if
   thresholds are not yet set in the local protocol.
6. **Confirm packages and versions.** The R `icd` package is archived -- MUST-AVOID. Use:
   - `medicalcoder` or `comorbidity` for Charlson/Elixhauser.
   - `PheWAS` (GitHub, not CRAN) for phecode/phecodeX grouping; phecodeX codes are
     character-prefixed -- keep them as strings.
   - `CDMConnector` or `FeatureExtraction` (OHDSI) for OMOP concept sets.
   Pin all versions in `renv.lock` (R) or `requirements.txt` (Python). Confirm CRAN/repo status
   at use -- tool maintenance changes; never assume a package is current.
7. **Handle local code systems explicitly.** Systems with no package (Japanese DPC / K-codes /
   YJ-codes, national ICD adaptations) require documented join tables against the official
   reference (MHLW, KEGG, UMLS). Do not approximate with a foreign vocabulary.
8. **Emit the manifest.** Produce the validated code-set manifest (see Output). Stop here and
   present it to the user before any downstream phenotype or analysis step.

## Pairs with (repo policy)

- `.claude/policies/health/code-mapping.md` (the rule this operationalizes).
- `secondary-data.md` (RECORD code-list reporting; provenance framing).
- `phenotyping.md` + `phenotype-gate` skill -- codes feed phenotypes; run map-clinical-codes first.
- `analysis/data-contracts.md` -- WARN/FAIL thresholds are set there; block on FAIL.
- `analysis/reproducibility.md` -- renv.lock pinning and transformation log.

## Rules / invariants

- Math by tool; anchor every code to source + version + extraction date. Never invent a code,
  a crosswalk number, or a mapping loss figure.
- One grouping system per variable; do not mix. Unmade grouping choices are
  PENDING_LOCAL_DECISION, not guesses.
- Crosswalk loss must be reported, not hidden. If the chain is lossy, say so and quantify it.
- Cleaning sequence is fixed -- steps cannot be reordered; document every deviation.
- Terminal-X in ICD-10-CM is structural -- preserve it. Only strip when the national extract
  explicitly documents admin-placeholder X usage.
- Never call an unaudited or externally-borrowed code list "validated" without stating the
  source audit; a portability check is required for local datasets.
- Package maintenance changes in months: check CRAN / upstream repo at use; `icd` is archived --
  avoid it unconditionally.

## Output

Emit a code-set manifest per `../_shared/spec-artifact.md`:

- **Typical (single vocabulary, single study):** one `metadata/<codeset-name>-manifest.md`
  carrying: declared source + version + extraction date; grouping approach chosen; crosswalk
  direction + % unmapped + % one-to-many; cleaning sequence applied (note any terminal-X or
  truncation decisions); validation gate results (% orphan / % unspecified / % truncated) with
  PASS / WARN / FAIL status; the transformation log (raw -> clean, logging every truncation); package names + versions; any PENDING_LOCAL_DECISION items flagged
  inline. Pair it with a minimal `<codeset-name>-render.qmd` that tables the manifest for the
  study record.
- **Large or multi-vocabulary:** split to an indexed `metadata/<codeset-name>/` directory with
  a `README.md` router, one section file per vocabulary, and a top-level `index.qmd` for the
  tabbed render -- apply judgment per `../_shared/spec-artifact.md`.
- **No Quarto (non-R stack):** ship the manifest `.md` only; skip the `.qmd`.
- The manifest is a frozen study input. Re-run and re-version it if the vocabulary or extraction
  date changes; never silently overwrite.
