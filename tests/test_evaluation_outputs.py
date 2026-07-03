"""Reproducibility checks for the evaluation results reported in the paper.

Runs scripts/run_evaluation.py end-to-end and verifies that the recomputed
metrics match both the stored result files and the headline numbers claimed
in the paper (Tables IV and V). Run with:  python -m pytest tests
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SUPP = ROOT / "supplementary"
METHODS = ["seed_heuristic", "flat_rule_screen", "explainable_precedence_screen"]
LABELS = ["clean", "ambiguity", "non_testability", "incompleteness"]

# Headline numbers claimed in the paper (abstract, Table IV, conclusion).
PAPER_CLAIMS = {
    "seed_heuristic": {"accuracy": 0.573, "macro_f1": 0.499},
    "flat_rule_screen": {"accuracy": 0.500, "macro_f1": 0.478},
    "explainable_precedence_screen": {"accuracy": 0.855, "macro_f1": 0.891},
}


@pytest.fixture(scope="module")
def recomputed():
    """Run the evaluation script exactly as a reviewer would."""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_evaluation.py")],
        capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert proc.returncode == 0, f"run_evaluation.py crashed:\n{proc.stderr}"
    return json.loads(proc.stdout)


def test_evaluation_script_produces_expected_keys(recomputed):
    assert set(recomputed) == set(METHODS)
    for m in METHODS:
        r = recomputed[m]
        for key in ["accuracy", "macro_precision", "macro_recall", "macro_f1", "per_class"]:
            assert key in r, f"{m} result is missing {key!r}"
        assert [p["label"] for p in r["per_class"]] == LABELS
        for p in r["per_class"]:
            for key in ["precision", "recall", "f1", "support", "tp", "fp", "fn"]:
                assert key in p


def test_recomputed_metrics_match_stored_results(recomputed):
    stored = json.loads((SUPP / "evaluation_results.json").read_text(encoding="utf-8"))
    for m in METHODS:
        for key in ["accuracy", "macro_precision", "macro_recall", "macro_f1"]:
            assert recomputed[m][key] == pytest.approx(stored[m][key], abs=1e-9), \
                f"{m}.{key} drifted from stored evaluation_results.json"
        assert recomputed[m]["per_class"] == stored[m]["per_class"]


def test_recomputed_metrics_match_summary_csv(recomputed):
    with open(SUPP / "evaluation_summary.csv", newline="", encoding="utf-8") as f:
        summary = {r["method"]: r for r in csv.DictReader(f)}
    assert set(summary) == set(METHODS)
    for m in METHODS:
        for key in ["accuracy", "macro_precision", "macro_recall", "macro_f1"]:
            assert float(summary[m][key]) == pytest.approx(recomputed[m][key], abs=5e-4)


def test_headline_numbers_match_paper_claims(recomputed):
    for m, claims in PAPER_CLAIMS.items():
        for key, value in claims.items():
            assert recomputed[m][key] == pytest.approx(value, abs=5e-4), \
                f"paper claims {m} {key}={value}, recomputed {recomputed[m][key]:.3f}"


def test_per_class_support_matches_gold_distribution(recomputed):
    supports = {p["label"]: p["support"]
                for p in recomputed["explainable_precedence_screen"]["per_class"]}
    assert supports == {"clean": 40, "ambiguity": 29,
                        "non_testability": 1, "incompleteness": 40}


def test_confusion_matrices_consistent_with_metrics(recomputed):
    for m in METHODS:
        with open(SUPP / f"confusion_matrix_{m}.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        header = rows[0][1:]
        diag = sum(int(row[1 + header.index(row[0])]) for row in rows[1:])
        assert diag / 110 == pytest.approx(recomputed[m]["accuracy"], abs=1e-9), \
            f"confusion_matrix_{m}.csv diagonal does not reproduce accuracy"
