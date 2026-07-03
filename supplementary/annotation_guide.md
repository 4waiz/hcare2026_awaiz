# Annotation Guide for Requirement Validation Study

## Goal
Label each requirement statement for quality defects. The paper evaluates whether an explainable LLM can help identify these defects while keeping a human reviewer in control.

## Unit of analysis
One row = one requirement statement.

## Primary labels
Use **one primary label** per row.

### 1. clean
The requirement is specific enough, testable enough, and not obviously ambiguous or incomplete.

**Example**
- "The system shall lock the account after 5 failed login attempts within 10 minutes."

### 2. ambiguity
The requirement uses vague or subjective wording that can support multiple interpretations.

**Common signals**
- easy, efficient, flexible, adequate, appropriate, secure, robust, minimal, quickly
- unclear actor or unclear scope
- "support" with no precise behavior

**Example**
- "The system shall be easily updatable for fixes and patches."

### 3. non_testability
The requirement cannot be objectively verified as written.

**Common signals**
- subjective success criteria
- no measurable acceptance condition
- quality claims without thresholds

**Example**
- "The interface should be user-friendly."

### 4. incompleteness
The requirement is missing a trigger, actor, value, condition, constraint, object, or completion of the sentence.

**Common signals**
- ends abruptly
- contains placeholders like TBD
- uses "etc." or "and/or"
- references missing external detail without enough context
- sentence ends with a colon and no list is included in the extracted row

**Example**
- "If transmission status indicates an error 10 consecutive times, the following actions shall"

### 5. conflict_candidate
Use only if a requirement clearly contradicts another requirement in the same document or corpus.
This label should usually be assigned while reviewing `conflict_candidates.csv`, not the main extraction file.

## Secondary notes
Use `review_notes` to explain why you changed the machine-seeded label.

## Reviewer workflow
1. Read the requirement text.
2. Decide whether the row is actually a requirement statement.
3. Assign `human_primary_label`.
4. If the row is not a valid requirement extraction, write that in `review_notes`.
5. For future LLM evaluation, set `accepted_by_human` after comparing model output to your decision.

## Recommended paper-safe subset
Start manual review with `requirements_goldset_curated.csv`.
It is smaller and cleaner than the full extraction file.