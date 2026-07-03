# Supplementary Material

Paper 15 — *Keeping Engineers in the Loop: Explainable Requirement Defect
Screening Across Software Requirements Specifications* — HCARE 2026, co-located
with IEEE RE 2026.

Repository: https://github.com/4waiz/hcare2026_awaiz

## Data provenance: 79 documents → 9,165 statements → 110 reviewed

1. **79 source documents** (`document_inventory.csv`, `processing_report.md`):
   mixed-format SRS documents (PDF, DOC, HTML, HTM, RTF) processed by a staged
   extraction pipeline.
2. **9,165 extracted requirement-like statements**
   (`requirements_extracted.csv`): first-pass extraction with machine-seeded
   labels. This is the *source pool* only — it is **not** manually evaluated
   ground truth.
3. **110-row manually reviewed gold set**
   (`reviewed_goldset_with_predictions.csv`): the curated subset that all metrics
   in the paper are computed on. One reviewer adjudicated every row
   (`human_primary_label`, see `annotation_guide.md` for the label definitions).
   The file also contains the predictions of the three screening conditions
   (`seed_heuristic`, `flat_rule_screen`, `explainable_precedence_screen`) plus
   the explainable screen's source span, rationale, rewrite guidance, and
   confidence for each row.

## Files

| File | Role |
|---|---|
| `requirements_extracted.csv` | Full extraction (9,165 rows) — source pool, not manually evaluated |
| `requirements_goldset_starter.csv` | 160-row machine-proposed starter set (pre-curation) |
| `requirements_goldset_curated.csv` | 110-row curated gold set (pre-prediction columns) |
| `reviewed_goldset_with_predictions.csv` | **Primary evaluation file**: 110 reviewed rows + all predictions |
| `representative_20_samples.csv` | The 20 cases shown in Table VI of the paper |
| `annotation_guide.md` | Label definitions and reviewer workflow used for adjudication |
| `evaluation_results.json` | Full metrics for the three conditions (Tables IV-V) |
| `evaluation_summary.csv` | One-line-per-condition summary (accuracy, macro P/R/F1) |
| `confusion_matrix_*.csv` | Confusion matrices (rows = human label, cols = predicted) |
| `conflict_candidates.csv` | 220 candidate contradiction pairs (review candidates only) |
| `document_inventory.csv` | Per-document inventory of the 79-document corpus |
| `processing_report.md` | Extraction pipeline report and known limitations |
| `llm_prompt_template.txt` | Prompt template for the LLM-assisted screening condition |

## Reproducing the metrics

```
python scripts/run_evaluation.py            # print metrics (stdlib only)
python scripts/run_evaluation.py --write    # also regenerate the result files
python scripts/generate_representative_samples.py   # regenerate the 20 samples
python -m pytest tests                      # verify package integrity + claims
```

## Notes for reviewers

- The paper reports metrics **only** on the 110-row reviewed gold set; the 9,165
  extracted statements are the pool the gold set was curated from.
- Non-testability has support 1 after review (several machine-seeded
  non-testability rows were relabeled during adjudication); its per-class metrics
  are unstable, as stated in the paper's limitations.
- The tool supports reviewer judgment and does not replace requirements
  engineers.
