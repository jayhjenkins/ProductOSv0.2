# /project:update-faq

## Add Entry to Living FAQ

Add a new question, answer, or update to the Living FAQ document. This can be triggered from any phase of the workflow.

## What to Do

1. **Locate the Living FAQ** in the initiative's package folder at `datasets/product/packages/{YYYY}/{slug}/living-faq.md`
   - List available package folders if the initiative is ambiguous
   - If no package folder or FAQ exists, inform the user and suggest running `/project:prep` first
3. **Ask the user** what they want to add or update:
   - New question? → Ask for: question text, source perspective, priority tag (blocking/important/tracked/deferred)
   - Answer to existing question? → Ask which question ID, then the answer
   - Update existing entry? → Ask which entry and what to change
4. **Write the update** to the Living FAQ
5. **Update the status counts** in the FAQ header
6. **Add a changelog entry** with the date and change description

## Priority Tags

| Tag | Meaning |
|-----|---------|
| `blocking` | Must be answered before PRD can be written |
| `important` | Should be answered before engineering begins |
| `tracked` | Good question, can be answered during development |
| `deferred` | Relevant for v2 or future iterations |

## Rules

- Any agent or the PM can ADD questions
- Only the PM can mark answers as FINAL
- Answers added by agents are marked as "DRAFT — PM review needed"
- Questions are organized by topic, not by when they were added
