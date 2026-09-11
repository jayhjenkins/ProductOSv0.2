---
name: recruiting-process-interview
description: Use when processing a completed PM interview  -  reads JD, resume, and transcript, generates a scored assessment via hiring-assess-pm-candidate, saves it to the candidate folder, and updates the opening's stackrank
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Process Interview

## Purpose

Transform raw interview materials into a structured, scored assessment and update the candidate stack rank:
- Read job description, resume, and interview transcript
- Apply the `hiring-assess-pm-candidate` framework across four dimensions
- Generate a complete assessment document
- Save assessment to the candidate folder
- Update `stackrank.md` with the candidate's scores and ranking

## When to Use

Activate when:
- User invokes `/recruiting:process-interview`
- An interview has been completed and the transcript is ready

---

## Workflow Steps

### 0. Ensure Folder Structure (self-scaffold)

This workflow operates on a folder layout under `datasets/recruiting/`. If that structure does not exist yet (no scaffolder skill has run), create the minimum needed before proceeding:

- If `datasets/recruiting/` does not exist, create it.
- If no opening folder exists for the opening you are processing, create `datasets/recruiting/<opening-slug>/` with stub `job-description.md` and `stackrank.md` files. The `stackrank.md` stub should carry frontmatter with `last_updated` and an empty rankings table (columns: Rank, Candidate, Recommendation, Tech, Team Fit, AI Fluency, Values, Interview Date, Notes).
- If no candidate folder exists for the candidate, create `datasets/recruiting/<opening-slug>/candidates/<candidate-slug>/` with stub `resume.md` and `interview-transcript.md` files.

Keep stubs minimal  -  a heading plus a one-line HTML comment marking them as awaiting content is enough. Then warn the user that any freshly created stub needs its content pasted in before a real assessment can be produced.

### 1. Select Job Opening

Scan `datasets/recruiting/` for subdirectories, excluding `templates/`.

Display the available openings and ask the user to select one.

### 2. Select Candidate

Scan `{opening-path}/candidates/` for subdirectories.

Display the available candidates and ask the user to select one.

### 3. Read Source Documents

Read all three source files from the candidate folder:

- `{opening-path}/job-description.md`
- `{opening-path}/candidates/{slug}/resume.md`
- `{opening-path}/candidates/{slug}/interview-transcript.md`

If any file is empty or missing content below the frontmatter comment, warn the user:

> "Warning: {filename} appears to be empty. Please paste the content and re-run."

Do not proceed with an empty source file.

### 4. Invoke hiring-assess-pm-candidate Skill

**Announce:** "I'm using hiring-assess-pm-candidate to evaluate {Candidate Name} for {Job Title}"

**Load:** `.claude/skills/hiring-assess-pm-candidate/SKILL.md`

**Apply the full framework:**
- Score Technical Experience Alignment (1-5) with evidence-backed narrative
- Score Team Fit (1-5) with evidence-backed narrative
- Score AI Fluency (1-5) with evidence-backed narrative
- Score Core Value Alignment (1-5) with evidence-backed narrative (against the company's core values read from the profile, or the generic anchors if none are configured)
- Apply recommendation guidance (Strong Yes / Weak Yes / Weak No / Strong No)
- Identify standout strengths (3 bullets)
- Identify red flags (or "None identified")

### 5. Generate Assessment Draft

Using the `pm-assessment-template.md` format from `datasets/recruiting/templates/`, produce a complete filled-in assessment:

- All frontmatter fields populated
- All four dimension scores and narratives filled in
- Overall Recommendation checked
- Summary paragraph written (2-3 sentences)
- Standout Strengths and Red Flags populated
- Final Recommendation paragraph written

**Display the draft assessment to the user.**

### 6. Ask for Adjustments

Ask the user:

> "Does any section need adjustment before I save this? (Enter the dimension name or 'none' to save as-is)"

If adjustments are requested: incorporate them and display the revised section. Repeat until the user is satisfied.

### 7. Save Assessment File

Save the finalized assessment as:

`{opening-path}/candidates/{slug}/{YYYY-MM-DD}-assessment.md`

Use today's date.

Report the saved path.

### 8. Read and Display Current Stackrank

Read `{opening-path}/stackrank.md` and display the current rankings table.

Present to the user:

> "Based on this assessment, where does {Candidate Name} rank among the candidates interviewed so far? (Enter a rank number, or 'bottom' to place at the end)"

### 9. Update Stackrank

Update the stackrank table in `{opening-path}/stackrank.md`:

- Insert the candidate at the specified rank position
- Shift other candidates' ranks accordingly
- Populate the row: Rank, Candidate name, Recommendation, Tech score, Team Fit score, AI Fluency score, Values score, Interview Date, Notes (1-2 sentence comment distilled from the assessment  -  the one thing that most distinguishes this candidate from the others)
- Update the `last_updated` frontmatter field to today's date

Report:

```
Assessment saved:
  {opening-path}/candidates/{slug}/{YYYY-MM-DD}-assessment.md

Stackrank updated:
  {opening-path}/stackrank.md
  {Candidate Name} ranked #{N} of {total} candidates
```

---

## Success Criteria

- All three source documents read without errors
- `hiring-assess-pm-candidate` framework fully applied  -  no dimension left unscored
- Assessment file saved to candidate folder with today's date
- User had opportunity to review and adjust before saving
- `stackrank.md` updated with new candidate row and refreshed `last_updated` date

## No Fabrication Policy

Scores and narratives must be grounded in evidence from the three source documents. Do not infer qualities that were not demonstrated. When evidence is thin, reflect that in a lower score and note the gap explicitly.

## Related Skills

**Invokes:**
- `hiring-assess-pm-candidate`: Provides the evaluation framework and rating anchors

**Reads:**
- `datasets/recruiting/templates/pm-assessment-template.md`

**Complementary to:**
- `recruiting-process-practicum`: The practicum is a separate signal from the interview. Run both, save both, let the stackrank reflect the integrated picture.
