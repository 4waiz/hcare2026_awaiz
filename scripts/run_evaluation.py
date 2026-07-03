#!/usr/bin/env python3
"""Recompute evaluation metrics from the manually reviewed 110-row gold set.

Reads supplementary/reviewed_goldset_with_predictions.csv (one row per
manually reviewed requirement, with the human adjudicated label and the
predictions of the three screening conditions) and recomputes accuracy,
per-class precision/recall/F1, and macro scores for each condition.

By default the metrics are printed as JSON to stdout. With --write, the
script also regenerates:
  - supplementary/evaluation_results.json
  - supplementary/evaluation_summary.csv
  - supplementary/confusion_matrix_<method>.csv (one per condition)

No third-party dependencies (Python 3.8+ standard library only).

Usage:  python scripts/run_evaluation.py [--write]
"""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDSET = ROOT / "supplementary" / "reviewed_goldset_with_predictions.csv"

LABELS = ["clean", "ambiguity", "non_testability", "incompleteness"]
METHODS = ["seed_heuristic", "flat_rule_screen", "explainable_precedence_screen"]


def metrics(y_true, y_pred):
    n = len(y_true)
    per = []
    for lab in LABELS:
        tp = sum((a == lab and b == lab) for a, b in zip(y_true, y_pred))
        fp = sum((a != lab and b == lab) for a, b in zip(y_true, y_pred))
        fn = sum((a == lab and b != lab) for a, b in zip(y_true, y_pred))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        per.append({"label": lab, "precision": prec, "recall": rec, "f1": f1,
                    "support": sum(a == lab for a in y_true),
                    "tp": tp, "fp": fp, "fn": fn})
    return {
        "accuracy": sum(a == b for a, b in zip(y_true, y_pred)) / n,
        "macro_precision": sum(p["precision"] for p in per) / len(LABELS),
        "macro_recall": sum(p["recall"] for p in per) / len(LABELS),
        "macro_f1": sum(p["f1"] for p in per) / len(LABELS),
        "per_class": per,
    }


def confusion(y_true, y_pred):
    """Rows = human gold label, columns = predicted label."""
    m = {t: {p: 0 for p in LABELS} for t in LABELS}
    for a, b in zip(y_true, y_pred):
        m[a][b] += 1
    return m


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="also regenerate the result files under supplementary/")
    args = parser.parse_args()

    with open(GOLDSET, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    y = [r["human_primary_label"] for r in rows]

    results = {m: metrics(y, [r[m] for r in rows]) for m in METHODS}
    print(json.dumps(results, indent=2))

    if args.write:
        out = ROOT / "supplementary"
        (out / "evaluation_results.json").write_text(
            json.dumps(results, indent=2), encoding="utf-8")
        with open(out / "evaluation_summary.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["method", "accuracy", "macro_precision", "macro_recall", "macro_f1"])
            for m in METHODS:
                r = results[m]
                w.writerow([m] + [round(r[k], 3) for k in
                                  ("accuracy", "macro_precision", "macro_recall", "macro_f1")])
        for m in METHODS:
            cm = confusion(y, [r[m] for r in rows])
            with open(out / f"confusion_matrix_{m}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([""] + LABELS)
                for t in LABELS:
                    w.writerow([t] + [cm[t][p] for p in LABELS])
        print(f"# wrote evaluation_results.json, evaluation_summary.csv and "
              f"confusion matrices under {out}")


if __name__ == "__main__":
    main()
