"""Artifact integrity checks for the HCARE 2026 reproducibility package.

These tests verify that every file the paper relies on is present and
internally consistent: the reviewed gold set, the 20 representative samples
shown in Table VI of the paper, the confusion matrices, and the annotation
guide. Run with:  python -m pytest tests
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPP = ROOT / "supplementary"

LABELS = {"clean", "ambiguity", "non_testability", "incompleteness"}
METHODS = ["seed_heuristic", "flat_rule_screen", "explainable_precedence_screen"]

REQUIRED_FILES = [
    "supplementary/requirements_goldset_curated.csv",
    "supplementary/reviewed_goldset_with_predictions.csv",
    "supplementary/representative_20_samples.csv",
    "supplementary/evaluation_results.json",
    "supplementary/evaluation_summary.csv",
    "supplementary/annotation_guide.md",
    "supplementary/llm_prompt_template.txt",
    "supplementary/document_inventory.csv",
    "supplementary/processing_report.md",
    "supplementary/confusion_matrix_seed_heuristic.csv",
    "supplementary/confusion_matrix_flat_rule_screen.csv",
    "supplementary/confusion_matrix_explainable_precedence_screen.csv",
    "scripts/run_evaluation.py",
    "scripts/generate_representative_samples.py",
    "figures/fig_macro_f1.png",
    "figures/fig_reviewed_distribution.png",
    "PACKAGE_MANIFEST.txt",
]


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_required_files_exist():
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).is_file()]
    assert not missing, f"missing package files: {missing}"


def test_goldset_has_110_manually_reviewed_rows():
    rows = read_csv(SUPP / "reviewed_goldset_with_predictions.csv")
    assert len(rows) == 110, "paper claims a 110-row manually reviewed gold set"


def test_goldset_has_expected_label_columns():
    rows = read_csv(SUPP / "reviewed_goldset_with_predictions.csv")
    for col in ["requirement_id", "requirement_text", "human_primary_label"] + METHODS:
        assert col in rows[0], f"gold set is missing column {col!r}"
    for row in rows:
        assert row["human_primary_label"] in LABELS
        for m in METHODS:
            assert row[m] in LABELS


def test_goldset_label_distribution_matches_paper_table_ii():
    rows = read_csv(SUPP / "reviewed_goldset_with_predictions.csv")
    counts = {}
    for row in rows:
        counts[row["human_primary_label"]] = counts.get(row["human_primary_label"], 0) + 1
    # Table II of the paper: 40 clean, 29 ambiguity, 1 non-testability, 40 incompleteness
    assert counts == {"clean": 40, "ambiguity": 29,
                      "non_testability": 1, "incompleteness": 40}


def test_representative_samples_has_exactly_20_rows():
    rows = read_csv(SUPP / "representative_20_samples.csv")
    assert len(rows) == 20


def test_representative_samples_have_required_columns():
    rows = read_csv(SUPP / "representative_20_samples.csv")
    required = {"sample_id", "requirement_id", "source_file", "requirement_excerpt",
                "gold_label", "explainable_screen_label", "flat_rule_screen_label",
                "explanation_cue", "suggested_reviewer_action"}
    assert required.issubset(rows[0].keys())
    ids = [r["sample_id"] for r in rows]
    assert len(set(ids)) == 20, "sample_id values must be unique"
    for row in rows:
        assert row["requirement_excerpt"].strip(), f"{row['sample_id']} has empty excerpt"
        assert row["explanation_cue"].strip()
        assert row["suggested_reviewer_action"].strip()


def test_representative_samples_cover_all_four_labels():
    rows = read_csv(SUPP / "representative_20_samples.csv")
    covered = {r["gold_label"] for r in rows}
    assert covered == LABELS, f"samples must cover all labels, got {covered}"


def test_representative_samples_trace_back_to_goldset():
    gold = {r["requirement_id"]: r
            for r in read_csv(SUPP / "reviewed_goldset_with_predictions.csv")}
    for row in read_csv(SUPP / "representative_20_samples.csv"):
        rid = row["requirement_id"]
        assert rid in gold, f"{rid} not in reviewed gold set"
        assert row["gold_label"] == gold[rid]["human_primary_label"]
        assert row["explainable_screen_label"] == gold[rid]["explainable_precedence_screen"]
        assert row["flat_rule_screen_label"] == gold[rid]["flat_rule_screen"]
        assert row["source_file"] == gold[rid]["file_name"]


def test_confusion_matrices_are_present_and_sum_to_110():
    for m in METHODS:
        path = SUPP / f"confusion_matrix_{m}.csv"
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 5, f"{path.name}: expected header + 4 label rows"
        assert rows[0][1:] == ["clean", "ambiguity", "non_testability", "incompleteness"]
        total = sum(int(c) for row in rows[1:] for c in row[1:])
        assert total == 110, f"{path.name}: cells must sum to the 110 reviewed rows"


def test_annotation_guide_defines_all_labels():
    text = (SUPP / "annotation_guide.md").read_text(encoding="utf-8")
    for label in ["clean", "ambiguity", "non_testability", "incompleteness"]:
        assert label in text, f"annotation guide does not define {label!r}"


def test_manifest_mentions_key_artifacts():
    text = (ROOT / "PACKAGE_MANIFEST.txt").read_text(encoding="utf-8")
    for name in ["reviewed_goldset_with_predictions.csv",
                 "representative_20_samples.csv",
                 "run_evaluation.py",
                 "SUBMIT_THIS_HCARE2026.docx",
                 "HCARE2026_Final.pdf"]:
        assert name in text, f"PACKAGE_MANIFEST.txt does not mention {name}"
