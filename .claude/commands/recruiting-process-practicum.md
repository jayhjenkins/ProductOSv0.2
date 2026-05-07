# /recruiting:process-practicum

## MANDATORY: Use the process-practicum Skill

**You MUST use the `process-practicum` skill located at `.claude/skills/recruiting-process-practicum/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using process-practicum to generate a PM practicum assessment"
2. **Read the skill**: Load `.claude/skills/recruiting-process-practicum/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Read the opening's practicum prompt and the candidate's practicum transcript; invoke the assess-pm-practicum framework; generate a complete scored assessment of product craft across five dimensions using a level matrix modeled on PM career ladders; save it to the candidate folder; and refresh the opening's stackrank Notes and rank position to reflect the practicum finding.

## Execution

The skill orchestrates:
1. Ask user to select job opening
2. Ask user to select candidate
3. Read practicum-prompt.md (opening folder) and practicum-transcript.md (candidate folder); optionally pull resume, interview transcript, and prior assessment for background context
4. Invoke assess-pm-practicum skill — score the five craft dimensions (Problem Framing & User Insight, Strategic Thinking & Vision, Prioritization & Tradeoffs, AI-First Product Thinking, Metrics & Outcomes) against the Craft Level Matrix. Each narrative must anchor its score to a matrix level. Session Dynamics is observational, not scored. Synthesize a Craft Level Read comparing demonstrated craft level to role level.
5. Generate complete assessment draft using pm-practicum-assessment-template.md
6. Display to user, incorporate any adjustments
7. Save as {YYYY-MM-DD}-practicum-assessment.md in candidate folder
8. Display current stackrank with an explicit read on how the practicum shifts the prior interview-only impression
9. Update stackrank.md — rank position and Notes column only; interview-scored columns (Tech / Team Fit / AI Fluency / Values) are left untouched

## When to Use

After a candidate has completed the live product practicum and you have the transcript. Typically this runs after `/recruiting:process-interview`, so the stackrank already has the candidate in it.
