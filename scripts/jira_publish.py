#!/usr/bin/env python3
"""
jira_publish.py — Parse a JIRA_DRAFT block from a task and publish to Jira
via a mini Claude session using the Jira MCP connector.

Called by the task server when the user clicks "Publish to Jira" in the UI.
"""

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import profile_lib

PM_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_jira_config():
    """Read Jira instance config from profile/integrations.yaml (see
    workflow-jira-home/SKILL.md's First-Run Setup). Never hardcode instance
    IDs here — they differ per Jira Cloud site and are discovered once,
    interactively, then written to the profile."""
    cfg = profile_lib.jira_config()
    if not cfg.get("cloud_id") or not cfg.get("project_key"):
        print(
            "Error: Jira is not configured yet. Run the workflow-jira-home skill "
            "interactively once (e.g. `/jira:create`) to complete first-run setup — "
            "it discovers your instance's IDs and writes them to profile/integrations.yaml.",
            file=sys.stderr,
        )
        sys.exit(1)
    return cfg


JIRA_CFG = _load_jira_config()
JIRA_CLOUD_ID = JIRA_CFG.get("cloud_id", "")
JIRA_PROJECT_KEY = JIRA_CFG.get("project_key", "")
JIRA_COMPONENT_ID = JIRA_CFG.get("component_id", "")
JIRA_AUTO_LABEL = JIRA_CFG.get("auto_label", "")  # optional swim-lane label, if your board uses one. Not auto-applied — drafts decide; see Swim Lane Rule in workflow-jira-home/SKILL.md.
JIRA_DEFAULT_ASSIGNEE = JIRA_CFG.get("default_assignee", "")  # default assignee accountId for top-level (Feature/Epic-role) types
CUSTOM_FIELDS = JIRA_CFG.get("custom_fields") or {}  # logical name -> Jira fieldId, discovered per-instance

# Canonical type names. Drafts that arrive with different casing or shorthand
# get normalized so Jira's case-sensitive issueTypeName check doesn't fail.
# Extend/override via profile if your instance uses different type names.
JIRA_TYPE_CANONICAL = {
    "bug": "Bug",
    "regression defect": "Regression Defect",
    "regression": "Regression Defect",
    "story": "Story",
    "unit": "Unit",
    "epic": "Epic",
    "feature": "Feature",
    "spike": "Spike",
    "hotfix": "Hotfix",
    "work item defect": "Work Item Defect",
    "performance defect": "Performance Defect",
    "security defect": "Security Defect",
}
for _role_cfg in (JIRA_CFG.get("issue_types") or {}).values():
    _name = (_role_cfg or {}).get("name")
    if _name:
        JIRA_TYPE_CANONICAL[_name.strip().lower()] = _name

# Types that use the top-level-name custom field (e.g. Feature/Epic Name).
# Derived from profile issue_types roles "top_level" and "epic", falling back
# to the common Jira defaults if unconfigured.
_ISSUE_TYPES = JIRA_CFG.get("issue_types") or {}
NAMED_PARENT_TYPES = {
    (_ISSUE_TYPES.get("top_level") or {}).get("name") or "Feature",
    (_ISSUE_TYPES.get("epic") or {}).get("name") or "Epic",
}


def normalize_type(raw):
    """Map common casings/shorthand to the canonical Jira issue type name."""
    if not raw:
        return "Bug"
    return JIRA_TYPE_CANONICAL.get(raw.strip().lower(), raw.strip())


# ─── Draft Parsing ───────────────────────────────────────────────────────────

def parse_jira_draft(body):
    """Extract JIRA_DRAFT fields from a task body string.

    Returns dict with: type, summary, description, priority, labels,
    release_notes, feature_name, gtm_date, client_commitment, parent.
    Returns None if no draft found.
    """
    if not body or "<!-- JIRA_DRAFT -->" not in body:
        return None

    # Extract the draft block
    match = re.search(r"<!-- JIRA_DRAFT -->(.+?)<!-- /JIRA_DRAFT -->", body, re.DOTALL)
    if not match:
        return None

    block = match.group(1)

    def _field(name):
        m = re.search(rf"<!-- {name}:(.+?) -->", block)
        return m.group(1).strip() if m else ""

    # JIRA_FEATURE_NAME is preferred; JIRA_EPIC_NAME accepted as legacy fallback.
    feature_name = _field("JIRA_FEATURE_NAME") or _field("JIRA_EPIC_NAME") or ""

    def _date_or_empty(name):
        # TBD and empty both mean "leave the Jira date field blank"
        raw = _field(name)
        return "" if raw.lower() == "tbd" else raw

    # Extract structured fields from HTML comments
    draft = {
        "type": normalize_type(_field("JIRA_TYPE") or "Bug"),
        "summary": _field("JIRA_SUMMARY") or "",
        "priority": _field("JIRA_PRIORITY") or "",
        "labels": [l.strip() for l in _field("JIRA_LABELS").split(",") if l.strip()],
        "release_notes": _field("JIRA_RELEASE_NOTES") or "",
        "feature_name": feature_name,
        # Kept for backwards-compatible callers; mirrors feature_name.
        "epic_name": feature_name,
        "gtm_date": _date_or_empty("JIRA_GTM_DATE"),
        "ea_date": _date_or_empty("JIRA_EA_DATE"),
        "spec_reference": _field("JIRA_SPEC_REFERENCE") or "",
        "client_commitment": _field("JIRA_CLIENT_COMMITMENT") or "",
        "parent": _field("JIRA_PARENT") or "",
        "assignee": _field("JIRA_ASSIGNEE") or "",
    }

    # Extract the description from the ### Description section
    desc_match = re.search(r"### Description\s*\n(.*?)(?=\n### |\n<!-- /JIRA_DRAFT)", block, re.DOTALL)
    if desc_match:
        draft["description"] = desc_match.group(1).strip()
    else:
        # Fallback: use everything between ### Summary and ### Fields
        fallback = re.search(r"### Summary\s*\n.*?\n(.*?)(?=\n### Fields|\n<!-- /JIRA_DRAFT)", block, re.DOTALL)
        draft["description"] = fallback.group(1).strip() if fallback else ""

    if not draft["summary"]:
        return None

    return draft


# ─── Claude Prompt Building ──────────────────────────────────────────────────

def build_claude_prompt(draft):
    """Build a constrained prompt for Claude to call the Jira MCP tool."""
    issue_type = normalize_type(draft.get("type") or "Bug")

    # Labels come straight from the draft. The skill's Swim Lane Rule decides
    # whether home_aidlc is present (Features/Epics yes; Bugs/Units/etc. no).
    # Dedupe only — preserve the draft's order and intent.
    seen = set()
    labels = []
    for l in (draft.get("labels") or []):
        if l and l not in seen:
            seen.add(l)
            labels.append(l)

    # Build additional_fields
    additional_fields = {
        "components": [{"id": JIRA_COMPONENT_ID}],
        "labels": labels,
    }

    if draft.get("priority"):
        additional_fields["priority"] = {"name": draft["priority"]}

    if draft.get("release_notes") and CUSTOM_FIELDS.get("release_notes"):
        additional_fields[CUSTOM_FIELDS["release_notes"]] = {"value": draft["release_notes"]}

    # Feature / Epic — use the discovered top-level-name custom field.
    if issue_type in NAMED_PARENT_TYPES:
        name = draft.get("feature_name") or draft.get("epic_name")
        if name and CUSTOM_FIELDS.get("top_level_name"):
            additional_fields[CUSTOM_FIELDS["top_level_name"]] = name
        if draft.get("gtm_date") and CUSTOM_FIELDS.get("target_date"):
            additional_fields[CUSTOM_FIELDS["target_date"]] = draft["gtm_date"]
        if draft.get("ea_date") and CUSTOM_FIELDS.get("early_access_date"):
            additional_fields[CUSTOM_FIELDS["early_access_date"]] = draft["ea_date"]
        if draft.get("spec_reference") and CUSTOM_FIELDS.get("spec_reference"):
            additional_fields[CUSTOM_FIELDS["spec_reference"]] = draft["spec_reference"]
        if draft.get("client_commitment") and CUSTOM_FIELDS.get("commitment"):
            additional_fields[CUSTOM_FIELDS["commitment"]] = [draft["client_commitment"]]

    # Parent link — typically for Unit → Feature/Epic. Jira accepts a top-level
    # `parent` key in additional_fields.
    parent_key = (draft.get("parent") or "").strip()
    if parent_key:
        additional_fields["parent"] = {"key": parent_key}

    # Assignee — top-level types default to the profile-configured default
    # assignee unless the draft overrides.
    assignee_id = (draft.get("assignee") or "").strip()
    if issue_type in NAMED_PARENT_TYPES:
        additional_fields["assignee"] = {"accountId": assignee_id or JIRA_DEFAULT_ASSIGNEE}
    elif assignee_id:
        additional_fields["assignee"] = {"accountId": assignee_id}

    additional_fields_json = json.dumps(additional_fields)

    # Escape for shell
    summary_escaped = draft["summary"].replace('"', '\\"')
    description_escaped = draft["description"].replace('"', '\\"')

    prompt = f"""You must call the mcp__claude_ai_Jira__createJiraIssue tool with EXACTLY these parameters. Do not modify any values. Do not add any extra fields. Just call the tool and report the result.

Call mcp__claude_ai_Jira__createJiraIssue with:
- cloudId: "{JIRA_CLOUD_ID}"
- projectKey: "{JIRA_PROJECT_KEY}"
- issueTypeName: "{issue_type}"
- summary: "{summary_escaped}"
- description: "{description_escaped}"
- contentFormat: "markdown"
- additional_fields: {additional_fields_json}

After the tool returns, output EXACTLY one line in this format:
JIRA_RESULT:ISSUE_KEY|ISSUE_URL

For example: JIRA_RESULT:{JIRA_PROJECT_KEY}-1234|https://{JIRA_CLOUD_ID}/browse/{JIRA_PROJECT_KEY}-1234

If the tool fails, output: JIRA_ERROR:description of what went wrong

Do not output anything else. No explanation, no markdown, no summary."""

    return prompt


# ─── Publishing ──────────────────────────────────────────────────────────────

def publish_to_jira(draft):
    """Spawn a mini Claude session to publish the draft to Jira.

    Returns (issue_key, issue_url) on success.
    Raises RuntimeError on failure.
    """
    prompt = build_claude_prompt(draft)

    # Strip Claude env vars (same pattern as handle_dispatch_task)
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE", "CMUX_CLAUDE"))}
    env["PATH"] = (
        os.path.join(os.path.expanduser("~"), ".local", "bin")
        + ":/opt/homebrew/bin"
        + ":" + env.get("PATH", "/usr/bin:/bin")
    )

    claude_bin = os.path.join(os.path.expanduser("~"), ".local", "bin", "claude")
    if not os.path.exists(claude_bin):
        claude_bin = "/opt/homebrew/bin/claude"

    try:
        result = subprocess.run(
            [claude_bin, "-p", prompt, "--max-turns", "3",
             "--allowedTools", "mcp__claude_ai_Jira__createJiraIssue"],
            cwd=PM_OS_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Claude session timed out after 120 seconds")

    output = result.stdout + "\n" + result.stderr

    # Parse result
    match = re.search(r"JIRA_RESULT:([^|\s]+)\|(\S+)", output)
    if match:
        return match.group(1), match.group(2)

    # Check for error
    err_match = re.search(r"JIRA_ERROR:(.+)", output)
    if err_match:
        raise RuntimeError(f"Jira creation failed: {err_match.group(1).strip()}")

    # Try to find issue key in output (fallback)
    key_match = re.search(rf"({re.escape(JIRA_PROJECT_KEY)}-\d+)", output)
    url_match = re.search(rf"(https://{re.escape(JIRA_CLOUD_ID)}/browse/{re.escape(JIRA_PROJECT_KEY)}-\d+)", output)
    if key_match:
        url = url_match.group(1) if url_match else f"https://{JIRA_CLOUD_ID}/browse/{key_match.group(1)}"
        return key_match.group(1), url

    raise RuntimeError(f"Could not parse Jira result from Claude output. Exit code: {result.returncode}. Output: {output[:500]}")


# ─── LangFuse Tracing ───────────────────────────────────────────────────────

def _trace_publish(task_id, draft, issue_key=None, issue_url=None, error=None):
    """Create a LangFuse trace for the publish operation."""
    try:
        from langfuse_client import create_trace
        create_trace(
            name="jira-publish",
            session_id=task_id,
            metadata={
                "jira_type": draft.get("type"),
                "jira_summary": draft.get("summary"),
            },
            tags=["jira", "publish"],
            input_data={
                "type": draft.get("type"),
                "summary": draft.get("summary"),
                "priority": draft.get("priority"),
                "labels": draft.get("labels"),
            },
            output_data={
                "issue_key": issue_key,
                "issue_url": issue_url,
                "error": error,
            },
        )
    except Exception:
        pass


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Publish a Jira draft from a PM-OS task")
    parser.add_argument("--task", required=True, help="Task ID (e.g., TASK-0123)")
    parser.add_argument("--dry-run", action="store_true", help="Parse and display draft without publishing")
    args = parser.parse_args()

    import task_lib
    task_data = task_lib.read_task(args.task)
    body = task_data.get("body", "")

    draft = parse_jira_draft(body)
    if draft is None:
        print("Error: No JIRA_DRAFT block found in task body", file=sys.stderr)
        sys.exit(1)

    # Labels submitted as-is (deduped). No auto-prepend — Swim Lane Rule lives
    # in the draft, not here.
    effective_labels = []
    for l in draft["labels"]:
        if l and l not in effective_labels:
            effective_labels.append(l)

    if not effective_labels:
        lane_hint = " ('everything else' column)"
    elif JIRA_AUTO_LABEL in effective_labels:
        lane_hint = " (AI DLC swim lane)"
    else:
        lane_hint = ""

    print(f"Parsed Jira Draft:")
    print(f"  Type:        {draft['type']}")
    print(f"  Summary:     {draft['summary']}")
    print(f"  Priority:    {draft['priority'] or '(default)'}")
    print(f"  Labels:      {', '.join(effective_labels) or '(none)'}{lane_hint}")
    print(f"  Release:     {draft['release_notes'] or '(none)'}")
    if draft.get("parent"):
        print(f"  Parent:      {draft['parent']}")
    if draft["type"] in NAMED_PARENT_TYPES:
        print(f"  {draft['type']} Name: {draft.get('feature_name') or draft.get('epic_name') or '(none)'}")
        print(f"  GTM Date:    {draft['gtm_date'] or '(none)'}")
        print(f"  EA Date:     {draft['ea_date'] or '(none)'}")
        print(f"  Spec Ref:    {draft['spec_reference'] or '(none)'}")
        print(f"  Commitment:  {draft['client_commitment'] or '(none)'}")
        assignee_display = draft.get("assignee") or (JIRA_DEFAULT_ASSIGNEE + " (profile default)" if JIRA_DEFAULT_ASSIGNEE else "(none)")
        print(f"  Assignee:    {assignee_display}")
    print(f"  Description: {draft['description'][:200]}...")

    if args.dry_run:
        print("\n[DRY RUN] Would publish with prompt:")
        print(build_claude_prompt(draft)[:500] + "...")
        return

    print("\nPublishing to Jira...")
    try:
        key, url = publish_to_jira(draft)
        print(f"\nSuccess! Created {key}: {url}")
        _trace_publish(args.task, draft, issue_key=key, issue_url=url)
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        _trace_publish(args.task, draft, error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
