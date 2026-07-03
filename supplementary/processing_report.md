# Processing report

## Input
Zip file: `req(1).zip`

## Inventory
- Total documents: 79
- PDFs: 62
- DOC files: 13
- HTML files: 2
- HTM files: 1
- RTF files: 1

## Extraction pipeline used
- PDF text extraction: `pdftotext` with fallback to `pypdf`
- DOC extraction: `antiword` with fallback to `LibreOffice`
- HTML parsing: `BeautifulSoup`
- RTF parsing: `pandoc` fallback

## Candidate extraction logic
Requirement-like statements were kept if they matched one of the following:
- contained normative modal language such as shall, must, or should
- or began with a likely system actor and contained an action verb

## Output summary
- Requirement-like statements extracted: 9165
- Machine-seeded ambiguity rows: 1336
- Machine-seeded non-testability rows: 606
- Machine-seeded incompleteness rows: 462
- Machine-seeded clean rows: 6761
- Starter gold set rows: 160
- Curated gold set rows: 110
- Conflict candidate pairs: 220

## Important limitations
- Some documents contain tables, numbering artifacts, and truncated lines.
- `requirements_extracted.csv` is a first-pass extraction, not fully human-cleaned ground truth.
- `requirements_goldset_curated.csv` is the best file to start manual annotation.
- `conflict_candidates.csv` contains review candidates, not verified contradictions.

## Recommended next step
1. Review `requirements_goldset_curated.csv`
2. Correct the human labels
3. Freeze the annotation guide
4. Run the plain LLM and explainable LLM conditions on the reviewed subset
5. Compute final metrics