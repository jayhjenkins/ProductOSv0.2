---
name: recruiting-process-practicum
description: Use when processing a completed PM practicum — reads the opening's practicum prompt and the candidate's practicum transcript, generates a scored assessment via assess-pm-practicum, saves it to the candidate folder, and updates the opening's stackrank notes
---

# Process Practicum

## Purpose

Transform a live product practicum into a structured, scored assessment of product craft:
- Read the opening's practicum prompt and the candidate's practicum transcript
- Apply the `assess-pm-practicum` framework — score five craft dimensions against a level matrix modeled on PM career ladders
- Generate a complete assessment document
- Save assessment to the candidate folder
- Offer to update `stackrank.md` with a refreshed rank and practicum-informed note

## When to Use

Activate when:
- User invokes `/recruiting:process-practicum`
- A product practicum has been completed and the transcript is ready

---

## Workflow Steps

### 1. Select Job Opening

Scan `~/pm-os/datasets/recruiting/` for subdirectories, excluding `templates/`.

Display the available openings and ask the user to select one.

### 2. Select Candidate

Scan `{opening-path}/candidates/` for subdirectories.

Display the available candidates and ask the user to select one.

### 3. Read Source Documents

Read the required source files:

- **Practicum prompt:** `{opening-path}/practicum-prompt.md`
- **Practicum transcript:** `{opening-path}/candidates/{slug}/practicum-transcript.md`

Also read for background context (optional — use for tie-breaks only, not primary evidence):

- `{opening-path}/job-description.md`
- `{opening-path}/candidates/{slug}/resume.md`
- `{opening-path}/candidates/{slug}/interview-transcript.md`
- Most recent `{opening-path}/candidates/{slug}/*-assessment.md` (if it exists)

If the practicum prompt or practicum transcript is empty or missing content below the frontmatter comment, warn the user:

> "Warning: {filename} appears to be empty. Please paste the content and re-run."

Do not proceed with an empty required source file.

### 4. Invoke assess-pm-practicum Skill

**Announce:** "I'm using assess-pm-practicum to evaluate {Candidate Name}'s practicum for {Job Title}"

**Load:** `.claude/skills/hiring-assess-pm-practicum/SKILL.md`

**Apply the full framework:**
- Score Problem Framing & User Insight (1–5) against the Craft Level Matrix, with evidence-backed narrative and explicit matrix-level reference
- Score Strategic Thinking & Vision (1–5) with evidence-backed narrative
- Score Prioritization & Tradeoffs (1–5) with evidence-backed narrative
- Score AI-First Product Thinking (1–5) with evidence-backed narrative
- Score Metrics & Outcomes (1–5) with evidence-backed narrative
- Write the Session Dynamics observational note (not scored — observational only)
- Synthesize the Craft Level Read (1 sentence: Foundational / Developing / Proficient / Strong / Exceptional, relative to the role level)
- Apply recommendation guidance (Strong Yes / Weak Yes / Weak No / Strong No) — compare demonstrated craft level to role level
- Identify standout moments (3 bullets)
- Identify concerns (or "None identified")

### 5. Generate Assessment Draft

Using the `pm-practicum-assessment-template.md` format from `~/pm-os/datasets/recruiting/templates/`, produce a complete filled-in assessment:

- All frontmatter fields populated
- All five dimension scores and narratives filled in, with each narrative explicitly referencing the Craft Level Matrix anchor ("This is a 3 because…")
- Overall Recommendation checked
- Summary paragraph and Craft Level Read written
- Standout Moments and Concerns populated
- Session Dynamics observational note written
- Final Recommendation paragraph written

**Display the draft assessment to the user.**

### 6. Ask for Adjustments

Ask the user:

> "Does any section need adjustment before I save this? (Enter the dimension name or 'none' to save as-is)"

If adjustments are requested: incorporate them and display the revised section. Repeat until the user is satisfied.

### 7. Save Assessment File

Save the finalized assessment as:

`{opening-path}/candidates/{slug}/{YYYY-MM-DD}-practicum-assessment.md`

Use today's date (or the `practicum_date` from the transcript frontmatter if present and not "TBD").

Report the saved path.

### 8. Read and Display Current Stackrank

Read `{opening-path}/stackrank.md` and display the current rankings table.

Summarize how the practicum should shift this candidate's position relative to the interview-only read. Be explicit about whether the practicum confirmed, raised, or lowered the earlier interview impression.

Present to the user:

> "Based on this practicum, where should {Candidate Name} now rank? (Enter a rank number, 'same' to keep current rank, or 'bottom' to place at the end)"

### 9. Update Stackrank

Update the stackrank table in `{opening-path}/stackrank.md`:

- Move the candidate to the specified rank position (or keep current if 'same')
- Shift other candidates' ranks accordingly
- Update the Notes column with a 1-2 sentence comment that folds in the practicum finding — specifically what the practicum revealed that the interview did not
- Update the `last_updated` frontmatter field to today's date

Do NOT change the existing Tech / Team Fit / AI Fluency / Values columns. Those are interview-scored. The practicum scores live in the practicum assessment file and inform the Notes column and the rank position, not the column values.

Report:

```
Practicum assessment saved:
  {opening-path}/candidates/{slug}/{YYYY-MM-DD}-practicum-assessment.md

Stackrank updated:
  {opening-path}/stackrank.md
  {Candidate Name} ranked #{N} of {total} candidates
  Notes updated to reflect practicum finding
```

---

## Success Criteria

- Practicum prompt and practicum transcript both read without errors
- `assess-pm-practicum` framework fully applied — no dimension left unscored
- Assessment file saved with the `-practicum-assessment.md` suffix so it is distinguishable from the interview assessment
- User had opportunity to review and adjust before saving
- `stackrank.md` Notes and rank refreshed; interview-scored columns left untouched
- `last_updated` date refreshed

## No Fabrication Policy

Scores and narratives must be grounded in evidence from the practicum prompt and transcript. The interview transcript and resume can inform tie-breaks and context but are not primary evidence for the practicum dimensions. When evidence is thin for a dimension, reflect that in a lower score and note the gap explicitly.

## Related Skills

**Invokes:**
- `assess-pm-practicum`: Provides the evaluation framework and rating anchors

**Depends on:**
- `setup-new-opening`: Created the opening folder
- `prep-interview`: Created the candidate folder

**Reads:**
- `datasets/recruiting/templates/pm-practicum-assessment-template.md`
- `datasets/recruiting/{opening}/practicum-prompt.md`
- `datasets/recruiting/{opening}/candidates/{slug}/practicum-transcript.md`

**Complementary to:**
- `process-interview`: The practicum is a separate signal from the interview. Run both, save both, let the stackrank reflect the integrated picture.
