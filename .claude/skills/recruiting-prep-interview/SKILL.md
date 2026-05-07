---
name: recruiting-prep-interview
description: Use when preparing for a PM candidate interview — creates the candidate folder and blank resume and transcript files inside the correct job opening
---

# Prep Interview

## Purpose

Scaffold a candidate folder inside an existing job opening:
- Let user select the relevant opening
- Prompt for the candidate's name and generate a slug
- Create the candidate subfolder with blank `resume.md` and `interview-transcript.md`

## When to Use

Activate when:
- User invokes `/recruiting:prep-interview`
- A new candidate needs folder setup before their interview

---

## Workflow Steps

### 1. List Existing Openings

Scan `~/pm-os/datasets/recruiting/` for subdirectories, excluding `templates/`.

Display the available openings:

```
Available job openings:
1. senior-product-manager_2026-02-23
2. principal-pm_2026-01-15
...

Which opening is this candidate interviewing for?
```

Wait for user selection.

### 2. Ask for Candidate's Full Name

Prompt the user:

> "What is the candidate's full name? (e.g., Jane Doe)"

Wait for response.

### 3. Generate Candidate Slug

**Slug rules:**
- Lowercase
- Replace spaces with hyphens
- Remove special characters
- Example: "Jane Doe" → `jane-doe`

**Candidate folder path:** `{opening-path}/candidates/{slug}/`

### 4. Create Candidate Folder Structure

Create:
- `{opening-path}/candidates/{slug}/`

### 5. Create Blank resume.md

Write `resume.md` with this frontmatter stub:

```markdown
---
candidate: {Full Name}
position: {Job Title from opening folder}
opening: {opening folder slug}
---

<!-- Paste the candidate's resume below this line -->
```

### 6. Create Blank interview-transcript.md

Write `interview-transcript.md` with this frontmatter stub:

```markdown
---
candidate: {Full Name}
position: {Job Title from opening folder}
opening: {opening folder slug}
interview_date: {YYYY-MM-DD}
interviewer: Jay Jenkins
---

<!-- Paste the interview transcript below this line -->
```

### 7. Report and Instruct

Report the paths created:

```
Candidate folder created:
  {opening-path}/candidates/{slug}/
  {opening-path}/candidates/{slug}/resume.md
  {opening-path}/candidates/{slug}/interview-transcript.md

Next steps:
  1. Paste the candidate's resume into resume.md
  2. After the interview, paste the transcript into interview-transcript.md
  3. Run /recruiting:process-interview to generate the assessment
```

---

## Success Criteria

- Candidate folder created inside the correct opening's `candidates/` directory
- `resume.md` exists with frontmatter stub, ready for resume content
- `interview-transcript.md` exists with frontmatter stub, ready for transcript
- User knows what to do next

## Related Skills

**Depends on:**
- `setup-new-opening`: Creates the opening folder this workflow writes into

**Related workflows:**
- `process-interview`: Reads these files to generate the assessment
