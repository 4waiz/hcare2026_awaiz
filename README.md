# Keeping Engineers in the Loop: Explainable Requirement Defect Screening Across Software Requirements Specifications

Reproducibility package for **Paper 15**, accepted at **HCARE 2026** (Workshop on
Human-Centered AI for Requirements Engineering), co-located with **IEEE RE 2026**.

**Authors:**
- Awaiz Ahmed — Al Ain University, United Arab Emirates — 202310183@aau.ac.ae
- Mohammad Umar — Al Ain University, United Arab Emirates — 202240077@aau.ac.ae

**Repository:** https://github.com/4waiz/hcare2026_awaiz

## What the paper reports

From a source corpus of **79 mixed-format SRS documents**, an extraction pipeline
produced **9,165 requirement-like statements**. This extraction corpus is a *source
pool*: it was **not** manually evaluated in full. For the evaluation reported in the
paper, a **gold set of 110 requirements** was curated and manually reviewed
(single-reviewer adjudication). Three screening conditions were compared on that
gold set:

| Condition | Accuracy | Macro-F1 |
|---|---|---|
| Seed heuristic | 0.573 | 0.499 |
| Flat rule screen | 0.500 | 0.478 |
| Explainable precedence-based screen | **0.855** | **0.891** |

The tool is designed for **triage and review support**. It supports reviewer
judgment; it does not replace requirements engineers.

## Folder structure

```
SUBMIT_THIS_HCARE2026.docx      Camera-ready paper (editable, IEEE format)
HCARE2026_Final.pdf             Camera-ready paper (PDF, letter size, <= 7 pages)
PACKAGE_MANIFEST.txt            File-by-file manifest
figures/                        Paper figures (PNG + PDF)
scripts/
  run_evaluation.py             Recomputes all reported metrics (stdlib only)
  generate_representative_samples.py  Regenerates the 20 Table VI samples
supplementary/                  Data, gold set, results, annotation guide (see its README)
tests/                          Pytest suite reviewers can run to verify the claims
```

## Reproduce the results

Requires Python 3.8+ (no third-party packages needed for the evaluation):

```
python scripts/run_evaluation.py
```

This recomputes accuracy, per-class precision/recall/F1, and macro scores for all
three screening conditions directly from
`supplementary/reviewed_goldset_with_predictions.csv`, and prints them as JSON.
The numbers match `supplementary/evaluation_results.json` and Tables IV-V of the
paper. Add `--write` to regenerate the stored result files and confusion matrices.

## Run the verification tests

```
pip install pytest
python -m pytest tests
```

The tests check that: all package files exist; the gold set has exactly 110
manually reviewed rows with the label distribution reported in Table II; the 20
representative samples (Table VI) exist, cover all four labels, and trace back to
the gold set row-by-row; the evaluation script runs and reproduces the stored
metrics and the paper's headline numbers; and the confusion matrices are
consistent with the reported accuracy.

## The 20 representative samples (Table VI)

`supplementary/representative_20_samples.csv` contains the exact 20 cases shown in
Table VI of the paper (6 ambiguity, 7 incompleteness, 1 non-testability, 6
clean/acceptable). Each row links back to the reviewed gold set via
`requirement_id` and includes the source document, the shortened excerpt used in
the paper, the gold label, the predictions of the explainable and flat-rule
screens, the explanation cue, and the suggested reviewer action. Regenerate it
with `python scripts/generate_representative_samples.py`.

## Ethical note

The screening workflow is an assistive triage aid. All labels in the gold set are
human decisions, the explainable screen exposes its rationale, source span, and
rewrite guidance precisely so a human reviewer can accept, reject, or correct each
flag, and the paper claims no autonomous requirement assessment capability.
