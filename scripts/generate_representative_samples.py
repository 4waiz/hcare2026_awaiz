#!/usr/bin/env python3
"""Generate supplementary/representative_20_samples.csv.

Selects 20 representative requirement screening examples from the manually
reviewed 110-row gold set (supplementary/reviewed_goldset_with_predictions.csv).
These are the same 20 cases shown in Table VI of the paper, so the paper table
and the repository file stay in sync by construction.

Selection covers all four gold labels:
  - 6 ambiguity, 7 incompleteness, 1 non-testability (the only gold instance),
    6 clean/acceptable
and includes mixed-cue cases (e.g., vague term + trailing colon) as well as an
over-flagging case where the flat rule screen mislabels a clean requirement.

Usage:  python scripts/generate_representative_samples.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDSET = ROOT / "supplementary" / "reviewed_goldset_with_predictions.csv"
OUTPUT = ROOT / "supplementary" / "representative_20_samples.csv"

MAX_FULL = 110   # texts at or below this length are kept whole
CUT = 92         # otherwise cut at a word boundary near this length

# (sample_id, requirement_id, expected_gold_label, excerpt_mode, explanation_cue, suggested_reviewer_action)
SELECTION = [
    ("S01", "940102af70_R0190", "ambiguity", "head",
     "vague adverb 'easily'", "Define measurable update criteria"),
    ("S02", "77c0a3eb3e_R0167", "ambiguity", "head",
     "subjective term 'appropriate'", "Specify help content per error class"),
    ("S03", "02085a94bf_R0019", "ambiguity", "head",
     "unquantified 'adequate'", "Set a numeric capacity threshold"),
    ("S04", "1aab4b911a_R0096", "ambiguity", "tail",
     "unbounded quality term 'secure'", "Reference concrete security controls"),
    ("S05", "0440128d89_R0104", "ambiguity", "head",
     "vague bound 'fast enough'", "Quantify maximum response latency"),
    ("S06", "940102af70_R0123", "ambiguity", "head",
     "subjective term 'intuitive'", "Define usability acceptance criteria"),
    ("S07", "63478ef7e0_R0047", "incompleteness", "tail",
     "trailing colon; command list missing", "Recover list from source document"),
    ("S08", "d0268483f8_R0176", "incompleteness", "head",
     "trailing colon (also vague 'easily')", "Complete installation-method list"),
    ("S09", "2dff23407b_R0070", "incompleteness", "tail",
     "placeholder 'xxx'", "Replace placeholder with target page"),
    ("S10", "acd39aad8f_R0128", "incompleteness", "head",
     "unfilled field '<xx hours/minutes>'", "Fill threshold and period"),
    ("S11", "b3fdf25c0f_R0311", "incompleteness", "tail",
     "sentence ends mid-clause", "Recover the missing action list"),
    ("S12", "5404d8a4d4_R0057", "incompleteness", "head",
     "ends at 'to aid in' boundary", "Complete purpose; name the actor"),
    ("S13", "69f4f47b18_R0283", "incompleteness", "head",
     "list introduction without list", "Attach the referenced item list"),
    ("S14", "d9e6063902_R0050", "non_testability", "head",
     "no verifiable behavior; hazard prose", "Rewrite as testable interlock requirement"),
    ("S15", "e63551dcc3_R0098", "clean", "head",
     "measurable threshold (0.1 s)", "Accept; verify with performance test"),
    ("S16", "348c2b1f7d_R0146", "clean", "head",
     "explicit availability window", "Accept; add uptime tolerance if needed"),
    ("S17", "deb4b8a723_R0146", "clean", "head",
     "observable admin actions; flat rule over-flags", "Accept; no rewrite needed"),
    ("S18", "710fbbd28b_R1455", "clean", "head",
     "quantified sustained rate", "Accept; verify in load test"),
    ("S19", "cf286cdcad_R0189", "clean", "head",
     "enumerated auditable events", "Accept; verify via log inspection"),
    ("S20", "63762168d3_R0242", "clean", "tail",
     "observable state maintenance", "Accept; no rewrite needed"),
]

FIELDS = [
    "sample_id", "requirement_id", "source_file", "requirement_excerpt",
    "gold_label", "explainable_screen_label", "flat_rule_screen_label",
    "explanation_cue", "suggested_reviewer_action",
]


def shorten(text, mode):
    text = " ".join(text.split())
    if len(text) <= MAX_FULL:
        return text
    if mode == "head":
        cut = text.rfind(" ", 0, CUT)
        return text[: cut if cut > 0 else CUT].rstrip(",;") + " ..."
    cut = text.find(" ", len(text) - CUT)
    return "... " + text[cut if cut > 0 else -CUT:].lstrip()


def main():
    with open(GOLDSET, newline="", encoding="utf-8") as f:
        gold = {row["requirement_id"]: row for row in csv.DictReader(f)}

    rows = []
    for sample_id, req_id, expected_label, mode, cue, action in SELECTION:
        if req_id not in gold:
            raise SystemExit(f"{req_id} not found in gold set")
        g = gold[req_id]
        if g["human_primary_label"] != expected_label:
            raise SystemExit(
                f"{req_id}: gold label {g['human_primary_label']!r} != expected {expected_label!r}")
        rows.append({
            "sample_id": sample_id,
            "requirement_id": req_id,
            "source_file": g["file_name"],
            "requirement_excerpt": shorten(g["requirement_text"], mode),
            "gold_label": expected_label,
            "explainable_screen_label": g["explainable_precedence_screen"],
            "flat_rule_screen_label": g["flat_rule_screen"],
            "explanation_cue": cue,
            "suggested_reviewer_action": action,
        })

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUTPUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
