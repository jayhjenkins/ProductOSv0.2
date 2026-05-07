---
name: recruiting-setup-new-opening
description: Use when creating a new PM job opening — scaffolds the folder structure, blank job description, and seeded stackrank file for a new hiring opening
---

# Setup New Opening

## Purpose

Scaffold a new PM job opening in the recruiting dataset:
- Prompt for job title and generate a URL-safe slug
- Create the dated opening folder and candidate subfolder
- Create a blank `job-description.md` ready for the JD to be pasted in
- Seed `stackrank.md` from the standard template

## When to Use

Activate when:
- User invokes `/recruiting:setup-opening`
- A new PM role is being opened and needs a tracking folder

---

## Workflow Steps

### 1. Ask for Job Title

Prompt the user:

> "What is the job title for this opening? (e.g., Senior Product Manager, Principal PM)"

Wait for response before proceeding.

### 2. Generate Slug and Path

**Slug rules:**
- Lowercase
- Replace spaces and special characters with hyphens
- Remove consecutive hyphens
- Example: "Senior Product Manager" → `senior-product-manager`

**Opening folder name:** `{slug}_{YYYY-MM-DD}` using today's date

**Full path:** `~/pm-os/datasets/recruiting/{slug}_{YYYY-MM-DD}/`

### 3. Create Folder Structure

Create:
- `~/pm-os/datasets/recruiting/{slug}_{YYYY-MM-DD}/`
- `~/pm-os/datasets/recruiting/{slug}_{YYYY-MM-DD}/candidates/`

### 4. Create Blank job-description.md

Write `job-description.md` inside the opening folder with this frontmatter stub:

```markdown
---
position: {Job Title}
opening: {slug}_{YYYY-MM-DD}
created: {YYYY-MM-DD}
---

<!-- Paste the full job description below this line -->
```

### 5. Seed stackrank.md

Write `stackrank.md` inside the opening folder:

```markdown
---
position: {Job Title}
created: {YYYY-MM-DD}
last_updated: {YYYY-MM-DD}
---

# Candidate Stack Rank: {Job Title}

| Rank | Candidate | Recommendation | Tech | Team Fit | AI Fluency | Values | Interview Date | Notes |
|------|-----------|----------------|------|----------|------------|--------|----------------|
|      |           |                |      |          |            |        |                |

---

## Notes

{Hiring context, open questions, timeline notes}
```

### 6. Report and Instruct

Report the paths created:

```
Opening created:
  ~/pm-os/datasets/recruiting/{slug}_{YYYY-MM-DD}/
  ~/pm-os/datasets/recruiting/{slug}_{YYYY-MM-DD}/candidates/
  ~/pm-os/datasets/recruiting/{slug}_{YYYY-MM-DD}/job-description.md
  ~/pm-os/datasets/recruiting/{slug}_{YYYY-MM-DD}/stackrank.md

Next step: Paste the full job description into job-description.md
```

---

## Success Criteria

- Opening folder and candidates subfolder created
- `job-description.md` exists with frontmatter stub, ready for content
- `stackrank.md` exists with seeded template and correct position/date metadata
- User knows what to do next

## Related Skills

**Related workflows:**
- `prep-interview`: Creates a candidate folder inside an existing opening
- `process-interview`: Generates assessment and updates stackrank
