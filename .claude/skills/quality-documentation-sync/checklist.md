# Documentation Sync Checklist

Use this checklist when creating or modifying skills to ensure all documentation remains consistent.

## Quick Reference: Skill Type → Documentation Files

| Skill Type | .claude/CLAUDE.md | CLAUDE.md | CURSOR-PM-SYSTEM.md | AGENTS.md | README.md | .cursor/rules/*.mdc |
|------------|-------------------|-----------|---------------------|-----------|-----------|---------------------|
| **Meta Skills** | ✓ Required | ✓ Required | ⚬ If architectural | ⚬ If user-facing | ⚬ If user needs | ✓ quality-gates.mdc (if QG) |
| **Quality Gates** | ✓ Required | ✓ Required | ⚬ If architectural | ✓ Required | ⚬ Brief mention | ✓ quality-gates.mdc |
| **Context Assembly** | ✓ Required | ✓ Required | ⚬ If architectural | ⚬ If user-facing | ⚬ If user needs | ✓ context-assembly.mdc |
| **Workflows** | ✓ Required | ✓ Required | ✓ Required | ✓ Required | ✓ Required | ✓ {domain}-workflows.mdc |

Legend:
- ✓ Required = Must update
- ⚬ Conditional = Update only if condition met

---

## Detailed Checklist by File

### 1. `.claude/CLAUDE.md` (Cursor-specific)

**Location**: `/Users/jjenkins11/Documents/superpowers-llm/.claude/CLAUDE.md`

**For Meta Skills:**
- [ ] Added to "Meta Skills" list (line ~80)
- [ ] Brief description included
- [ ] Related skills cross-referenced

**For Quality Gates:**
- [ ] Added to "Quality Gates" list (line ~85-91)
- [ ] Brief description of validation purpose
- [ ] Pass/fail criteria mentioned

**For Context Assembly:**
- [ ] Added to "Context Assembly" list (line ~93-97)
- [ ] Brief description of what context is gathered
- [ ] Input/output format noted

**For Workflows:**
- [ ] Added to "Workflows" list (line ~106-118)
- [ ] Slash command mapping added to "Commands" section (line ~144-161)
- [ ] Brief description of workflow purpose

---

### 2. `CLAUDE.md` (Root-level, Claude Code)

**Location**: `/Users/jjenkins11/Documents/superpowers-llm/CLAUDE.md`

**For Meta Skills:**
- [ ] Added to "Meta Skills" category (line ~18)
- [ ] Brief description in parentheses

**For Quality Gates:**
- [ ] Added to "Quality Gates" category (line ~19)
- [ ] Validation purpose described

**For Context Assembly:**
- [ ] Added to "Context Assembly" category (line ~20)
- [ ] Context gathering purpose described

**For Workflows:**
- [ ] Added to "Workflows" category (line ~22)
- [ ] Slash command added to "Slash Commands → Skills Mapping" (line ~36-46)
- [ ] Added to relevant "Core Commands" section (line ~48-131)

---

### 3. `CURSOR-PM-SYSTEM.md` (Architecture)

**Location**: `/Users/jjenkins11/Documents/superpowers-llm/CURSOR-PM-SYSTEM.md`

**Only update if:**
- New workflow category (major capability addition)
- Changes system architecture significantly
- Affects agent/mode behavior

**If updating:**
- [ ] Added to "Rules" table description (line ~27-38)
- [ ] Added to "Key Workflows" section (line ~40-104)
- [ ] Workflow steps documented
- [ ] Integration points noted

---

### 4. `AGENTS.md` (Agent capabilities)

**Location**: `/Users/jjenkins11/Documents/superpowers-llm/AGENTS.md`

**For User-Facing Workflows:**
- [ ] Added to relevant agent's "Capabilities" section (line ~13-20)
- [ ] Added to "Example Prompts" section (line ~30-54)
- [ ] Added to "Output Locations" if creates files (line ~56-63)
- [ ] Added to "Choosing the Right Agent" routing table (line ~187-206)

**For Quality Gates:**
- [ ] Added to "Quality Standards All Agents Follow" (line ~210-234)
- [ ] Brief description of what is validated
- [ ] Enforcement mechanism noted

---

### 5. `README.md` (Main documentation)

**Location**: `/Users/jjenkins11/Documents/superpowers-llm/README.md`

**For User-Facing Workflows:**
- [ ] Added to relevant agent description (line ~14-37)
- [ ] Added to "Key Workflows" section (line ~56-94)
- [ ] Workflow diagram/steps included
- [ ] Added to "Example Prompts" section (line ~147-168)
- [ ] File locations updated if needed (line ~39-54)

**For Quality Gates:**
- [ ] Brief mention in "Quality Standards" section (line ~98-125)
- [ ] Linked to detailed documentation

---

### 6. `.cursor/rules/*.mdc` (Cursor workflow definitions)

**Location**: `/Users/jjenkins11/Documents/superpowers-llm/.cursor/rules/`

**Choose the appropriate file:**
- `core-system.mdc` — System-wide behavior, file structure, safety rails
- `product-workflows.mdc` — Product planning, PRDs, roadmap updates, CS prep
- `metrics-workflows.mdc` — Metrics analysis workflows
- `strategy-workflows.mdc` — Strategy sessions, decision memos
- `research-workflows.mdc` — Research processing, context gathering
- `quality-gates.mdc` — Quality validation rules
- `context-assembly.mdc` — Context gathering patterns

**For Workflows:**
- [ ] Added workflow section with complete description
- [ ] Workflow steps documented in detail
- [ ] Quality gates referenced
- [ ] Success criteria defined
- [ ] File locations specified
- [ ] Integration points noted

**For Quality Gates:**
- [ ] Added to `quality-gates.mdc`
- [ ] Pass/fail criteria defined
- [ ] Iron laws stated
- [ ] Anti-rationalization blocks included

**For Context Assembly:**
- [ ] Added to `context-assembly.mdc`
- [ ] Input sources defined
- [ ] Output format specified
- [ ] Normalization rules documented

---

## Validation Questions

After completing updates, verify:

### Discoverability Check
- [ ] If a user reads only `.claude/CLAUDE.md`, would they know this skill exists?
- [ ] If a user reads only `CLAUDE.md`, would they know how to use it?
- [ ] If a user reads only `README.md`, would they discover the capability?

### Usability Check
- [ ] If a user reads `AGENTS.md`, would they know which agent to use?
- [ ] Are example prompts clear and actionable?
- [ ] Are file locations accurately documented?

### Technical Check
- [ ] If a Cursor agent loads the relevant `.mdc` file, would it have complete instructions?
- [ ] Is `CURSOR-PM-SYSTEM.md` accurately describing the system architecture?
- [ ] Are all cross-references valid (skill names match)?

### Consistency Check
- [ ] Skill name is identical across all files?
- [ ] Descriptions are contextually appropriate for each file?
- [ ] Slash command mappings are consistent?
- [ ] No broken internal links?

---

## Example: Documentation Updates for a Workflow Skill

**Skill**: `launch-announcement` (workflow)
**Domain**: Product management

### Files Updated:
1. ✓ `.claude/CLAUDE.md` — Added to Workflows list (line 118) and Commands index (line 146)
2. ✓ `CLAUDE.md` — Added to Workflows category and Core Commands
3. ✓ `CURSOR-PM-SYSTEM.md` — Not updated (not architecturally significant)
4. ✓ `AGENTS.md` — Added to Product Strategist capabilities, example prompts, output locations, routing table
5. ✓ `README.md` — Added to Product Strategist description, workflow section, example prompts
6. ✓ `.cursor/rules/product-workflows.mdc` — Added complete Launch Announcement workflow section

**Reference**: See `docs/launch-announcement-implementation.md` for detailed documentation of what was updated.

---

## Anti-Patterns to Avoid

❌ **Updating only the first file you think of**
→ Use the full matrix to identify all required files

❌ **Copy-pasting identical text to all files**
→ Adapt descriptions to each file's context and audience

❌ **Skipping .mdc files because they're "just Cursor"**
→ Cursor agents depend on these files for workflow execution

❌ **Adding skill name but not description/examples**
→ Each file needs contextually appropriate detail

❌ **Forgetting to update example prompts**
→ Users discover capabilities through examples

❌ **Not validating cross-references**
→ Broken links frustrate users and agents

---

## Success Criteria

Documentation sync is complete when:
- ✓ All required files (per matrix) have been updated
- ✓ All validation questions answered "yes"
- ✓ Cross-references validated and working
- ✓ No anti-patterns present
- ✓ Skill is discoverable through multiple documentation paths
- ✓ Both Cursor and Claude Code agents can find and use the skill

