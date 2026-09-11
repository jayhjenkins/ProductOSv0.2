"""Single source of truth for per-person profile facts.

The engine reads identity and integration values ONLY through this module.
Resolves the active profile dir as profile/ if present, else profile.example/.
"""
import json
import os
import tempfile
from ruamel.yaml import YAML

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PM_OS_DIR = os.path.dirname(SCRIPT_DIR)

_yaml = YAML(typ="safe")

# Round-trip loader/dumper for WRITES: preserves comments + formatting so the
# helpful annotations in the profile YAML files survive a setter mutating one key.
_yaml_rt = YAML()
_yaml_rt.preserve_quotes = True


def profile_dir(root=None):
    root = root or PM_OS_DIR
    live = os.path.join(root, "profile")
    if os.path.isdir(live):
        return live
    return os.path.join(root, "profile.example")


def _load_yaml(name, root=None):
    path = os.path.join(profile_dir(root), name)
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return _yaml.load(f) or {}


def profile(root=None):
    return _load_yaml("profile.yaml", root)


def integrations(root=None):
    return _load_yaml("integrations.yaml", root)


def config(root=None):
    return _load_yaml("config.yaml", root)


def display_name(root=None):
    return profile(root).get("display_name") or "Operator"


def email(root=None):
    return profile(root).get("email", "")


def company(root=None):
    return profile(root).get("company", "")


def persona(root=None):
    return profile(root).get("persona") or "pm"


def integration(name, root=None):
    return integrations(root).get(name) or {}


def provider(name, root=None):
    return integration(name, root).get("provider") or "none"


def transcript_config(root=None):
    t = integration("transcript", root)
    return {
        "provider": t.get("provider") or "none",
        "target": t.get("target") or "datasets/meetings/",
        "external_feed": bool(t.get("external_feed", False)),
    }


def transcript_state_dir(root=None):
    """Per-person runtime dir for transcript creds/session/ledger (gitignored)."""
    return os.path.join(profile_dir(root), "transcript")


def jira_config(root=None):
    pm = integration("project_management", root)
    if pm.get("provider") != "jira":
        return {}
    return pm.get("jira") or {}


def doc_sync_config(root=None):
    d = integration("doc_sync", root)
    return {
        "onedrive_root": d.get("onedrive_root", ""),
        "sharepoint_site": d.get("sharepoint_site", "PM-OS"),
        "enabled": bool(d.get("enabled", False)),
    }


def eos_sheet(root=None):
    """The read-only EOS sheet locator (an M365/SharePoint resource), or None.

    Read by the sheet-watch sentinel; the EOS sheet is manual-on-purpose and is
    NEVER written. The locator lives in the per-person profile, never in the
    engine (invariant #1); unconfigured -> None -> sheet-watch runs blind."""
    return integration("eos", root).get("sheet") or None


def _analytics(name, root=None):
    return (integrations(root).get("analytics") or {}).get(name) or {}


def pendo_config(root=None):
    p = _analytics("pendo", root)
    return {"provider": p.get("provider") or "none",
            "subscription_id": p.get("subscription_id", ""),
            "app_ids": p.get("app_ids") or {}}


def databricks_config(root=None):
    d = _analytics("databricks", root)
    return {"provider": d.get("provider") or "none",
            "catalog": d.get("catalog", ""),
            "sources": d.get("sources") or {}}


def model(role, default=None, root=None):
    return (config(root).get("models") or {}).get(role, default)


def server_port(root=None):
    return int((config(root).get("server") or {}).get("port", 8742))


def voice_path(channel, root=None):
    return os.path.join(profile_dir(root), "voice", f"{channel}.md")


def voice_text(channel=None, root=None):
    """Return voice guidance. channel='teams'|'email', or None for both concatenated."""
    channels = [channel] if channel else ["teams", "email"]
    chunks = []
    for ch in channels:
        path = voice_path(ch, root)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                chunks.append(f.read().strip())
    return "\n\n".join(chunks)


CAPABILITIES_SCHEMA_VERSION = 1


def read_capabilities(root=None):
    """Read profile/capabilities.json, returning an empty-but-valid doc if absent."""
    path = os.path.join(profile_dir(root), "capabilities.json")
    if not os.path.isfile(path):
        return {"schema_version": CAPABILITIES_SCHEMA_VERSION, "capabilities": {}}
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {"schema_version": CAPABILITIES_SCHEMA_VERSION, "capabilities": {}}
    data.setdefault("schema_version", CAPABILITIES_SCHEMA_VERSION)
    data.setdefault("capabilities", {})
    return data


def write_capabilities(data, root=None):
    """Atomically write capabilities.json into the live profile dir."""
    data.setdefault("schema_version", CAPABILITIES_SCHEMA_VERSION)
    target = os.path.join(profile_dir(root), "capabilities.json")
    dir_ = os.path.dirname(target)
    fd, tmp = tempfile.mkstemp(prefix=".capabilities-", dir=dir_)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _atomic_write_text(name, text, root=None):
    """Atomically write text to <profile_dir>/name (mkstemp + os.replace)."""
    target = os.path.join(profile_dir(root), name)
    dir_ = os.path.dirname(target)
    os.makedirs(dir_, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".profile-", dir=dir_)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _update_yaml(name, mutate, root=None):
    """Round-trip read-modify-write of a profile YAML file.

    Loads with the round-trip loader (preserving comments/formatting), calls
    mutate(doc) to change in place, and writes the result back atomically.
    Mutating only the targeted key leaves all siblings + comments intact.
    """
    path = os.path.join(profile_dir(root), name)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            doc = _yaml_rt.load(f)
        if doc is None:
            doc = {}
    else:
        doc = {}
    mutate(doc)
    import io
    buf = io.StringIO()
    _yaml_rt.dump(doc, buf)
    _atomic_write_text(name, buf.getvalue(), root)


def write_identity(data, root=None):
    """Update identity fields in profile.yaml from data, preserving everything else.

    Only display_name/email/company/timezone are written (when present in data);
    unknown keys are ignored and existing keys like persona are never clobbered.
    """
    def mutate(doc):
        for key in ("display_name", "email", "company", "timezone"):
            if key in data:
                doc[key] = data[key]
    _update_yaml("profile.yaml", mutate, root)


def write_voice(channel, text, root=None):
    """Atomically write voice/{channel}.md, creating the file if missing."""
    _atomic_write_text(os.path.join("voice", f"{channel}.md"), text, root)


def set_transcript_external(value, root=None):
    """Set integrations.yaml transcript.external_feed = bool(value).

    Records that the transcript feed is served by an EXTERNAL, already-working
    downloader (e.g. a prior install's Otter LaunchAgent re-pointed at Magnolia's
    otter_sync.py) rather than a fresh in-Magnolia setup. When true, the Doctor
    verifies the feed by output marker instead of nagging about Playwright/otterai
    deps. Preserves the transcript sub-config + siblings + comments."""
    def mutate(doc):
        t = doc.get("transcript")
        if not isinstance(t, dict):
            t = {}
            doc["transcript"] = t
        t["external_feed"] = bool(value)
    _update_yaml("integrations.yaml", mutate, root)


def transcript_external(root=None):
    """True if the transcript feed is served by an external downloader."""
    return transcript_config(root)["external_feed"]


def set_integration_provider(category, provider_id, root=None):
    """Set integrations.yaml[category]['provider'], preserving sub-config + siblings."""
    def mutate(doc):
        cat = doc.get(category)
        if not isinstance(cat, dict):
            cat = {}
            doc[category] = cat
        cat["provider"] = provider_id
    _update_yaml("integrations.yaml", mutate, root)


def set_integration_conventions(category, text, provider=None, root=None):
    """Write free-form team conventions into integrations.yaml.

    Conventions are fuzzy team nuance that has no structured field (e.g. "always
    set the Sprint field", "bug titles prefixed [Area]"). They live in the PROFILE,
    never in a generated artifact, so the artifact stays denylist-clean and the
    nuance stays editable. With provider set, nests under
    <category>.<provider>.conventions (so jira_config()['conventions'] surfaces it);
    otherwise <category>.conventions. Siblings + comments are preserved."""
    def mutate(doc):
        cat = doc.get(category)
        if not isinstance(cat, dict):
            cat = {}
            doc[category] = cat
        target = cat
        if provider:
            sub = cat.get(provider)
            if not isinstance(sub, dict):
                sub = {}
                cat[provider] = sub
            target = sub
        target["conventions"] = text
    _update_yaml("integrations.yaml", mutate, root)


def set_integration_confirmed(category, confirmed, provider=None, root=None):
    """Set the Tier-2 consent flag integrations.yaml[category][provider]['confirmed'].

    'confirmed' records that the operator okayed this integration to write to the
    OUTSIDE WORLD. With provider given, nests under <category>.<provider>.confirmed
    (creating the sub-block if absent); otherwise <category>.confirmed. Siblings +
    comments are preserved."""
    def mutate(doc):
        cat = doc.get(category)
        if not isinstance(cat, dict):
            cat = {}
            doc[category] = cat
        target = cat
        if provider:
            sub = cat.get(provider)
            if not isinstance(sub, dict):
                sub = {}
                cat[provider] = sub
            target = sub
        target["confirmed"] = bool(confirmed)
    _update_yaml("integrations.yaml", mutate, root)


def set_active_packs(packs, root=None):
    """Set config.yaml['active_skill_packs'] to the given list."""
    def mutate(doc):
        doc["active_skill_packs"] = list(packs)
    _update_yaml("config.yaml", mutate, root)


def set_cost_posture(level, root=None):
    """Set config.yaml['models']['cost_posture'], preserving sibling model keys."""
    def mutate(doc):
        models = doc.get("models")
        if not isinstance(models, dict):
            models = {}
            doc["models"] = models
        models["cost_posture"] = level
    _update_yaml("config.yaml", mutate, root)


def profile_is_live(root=None):
    """True if the live profile/ dir exists (not the profile.example fallback)."""
    root = root or PM_OS_DIR
    return os.path.isdir(os.path.join(root, "profile"))


def onboarding_complete(root=None):
    """True once onboarding has finished: the live profile exists AND its config
    carries `onboarded: true`. NOT mere profile/ existence (meta-onboard creates
    profile/ early, at step 0, so existence alone would flip the gate
    mid-onboarding)."""
    if not profile_is_live(root):
        return False
    try:
        return bool(config(root=root).get("onboarded"))
    except Exception:
        # A malformed config.yaml must not crash the gate. Treat an unreadable
        # config as "not complete" - the safe direction, gating to onboarding.
        return False


def mark_onboarded(root=None):
    """Stamp `onboarded: true` into the live profile config (the completion
    marker). Called by meta-onboard's final step. Uses the same round-trip
    read-modify-write idiom every other config setter uses, preserving siblings
    and comments.

    No-op (no write) when there is no live profile/. Without this guard a call
    with no live profile would fall through profile_dir()'s profile.example
    fallback and stamp the SHIPPED template - dirtying the tree and making every
    fresh clone skip onboarding. A silent no-op is the safe behavior for a marker
    writer; this mirrors the profile_is_live guard its sibling setters rely on."""
    if not profile_is_live(root):
        return
    def mutate(doc):
        doc["onboarded"] = True
    _update_yaml("config.yaml", mutate, root)


def migrate_legacy_onboarded(root=None):
    """Backward-compat: an existing install (live profile already populated with
    a real identity) predates the marker - stamp it so it is never re-gated into
    onboarding. Returns True if it stamped, False otherwise. Idempotent."""
    if not profile_is_live(root):
        return False
    cfg = config(root=root)
    if cfg.get("onboarded"):
        return False
    name = (profile(root=root).get("display_name") or "").strip()
    placeholder = name == "" or name.lower() in ("your name", "name")
    if placeholder:
        return False   # genuinely fresh/example-shaped; let onboarding run
    mark_onboarded(root=root)
    return True


def autonomy_enforcement(root=None):
    """Global posture flag: may an autonomous action-type auto-ship without a
    per-instance human approve? Default False (auto-ship is opt-in per install)."""
    return bool(config(root).get("autonomy_enforcement", False))


def set_autonomy_enforcement(enabled, root=None):
    """Set config.yaml['autonomy_enforcement'] (preserves siblings + comments)."""
    def mutate(doc):
        doc["autonomy_enforcement"] = bool(enabled)
    _update_yaml("config.yaml", mutate, root)


def configured_server_port(root=None):
    """The EXPLICITLY-configured server port as an int, or None if unset.

    Distinct from server_port(), which applies the 8742 default. Returns None
    when no port has been deliberately chosen, so callers can tell "the operator
    chose a port" apart from "fall back to the default".

    A port counts as explicit ONLY when it lives in the operator's LIVE profile/.
    Without this guard, profile_dir() falls back to the shipped profile.example/
    (which carries server.port: 8742), so a brand-new install with no live
    profile/ would read that template port and look like a deliberate 8742 choice
    - defeating the launcher's auto-free-port hunt and colliding with whatever is
    already on 8742 (e.g. an existing production board)."""
    if not profile_is_live(root):
        return None
    p = (config(root).get("server") or {}).get("port")
    return int(p) if p is not None else None


def set_server_port(p, root=None):
    """Persist server.port = int(p) into the LIVE profile config.

    Ensures the live profile/ dir exists FIRST: _update_yaml writes through
    profile_dir(), which falls back to the TRACKED profile.example/ when no
    live profile/ exists (the same trap mark_onboarded guards). Without this
    a fresh install would dirty the shipped template. Preserves any existing
    server subkeys plus all sibling top-level keys + comments."""
    os.makedirs(os.path.join(root or PM_OS_DIR, "profile"), exist_ok=True)

    def mutate(doc):
        server = doc.get("server") or {}
        server["port"] = int(p)
        doc["server"] = server
    _update_yaml("config.yaml", mutate, root)


TIER_ORDER = ["light", "standard", "deep"]
TIER_MODELS = {
    "light": "haiku",
    "standard": "sonnet",
    "deep": "opus",
}
CODEX_TIER_MODELS = {
    "light": "gpt-5.6-luna",
    "standard": "gpt-5.6-terra",
    "deep": "gpt-5.6-sol",
}
HARNESS_TIER_MAPS = {
    "claude": TIER_MODELS,
    "codex": CODEX_TIER_MODELS,
}
_POSTURE_SHIFT = {"low": -1, "balanced": 0, "high": 1}
_DEFAULT_TIER = "standard"


def harness(root=None):
    """The active CLI harness: 'claude' (default) or 'codex'."""
    return (config(root).get("harness") or "claude").lower()


def set_harness(value, root=None):
    """Set config.yaml['harness'], preserving siblings + comments."""
    def mutate(doc):
        doc["harness"] = value
    _update_yaml("config.yaml", mutate, root)


def cost_posture(root=None):
    return (config(root).get("models") or {}).get("cost_posture") or "balanced"


def resolve_model(worker_tier, posture=None, task_override=None, root=None,
                   min_tier=None):
    """Resolve the model id for a dispatch.

    Precedence: task_override (a model id OR a tier name) wins. Otherwise the
    worker's declared tier is shifted by the posture (low -1 / balanced 0 /
    high +1) and clamped to [light, deep]. Unknown tier -> 'standard';
    unknown posture -> 'balanced'. The active harness determines the
    tier-to-model mapping (Claude vs Codex model families).

    min_tier: optional floor (e.g. 'standard') — the resolved tier will never
    drop below this regardless of posture shift. Used by dispatch paths that
    require a minimum capability (MCP tool calling, structured output)."""
    active = harness(root)
    tier_map = HARNESS_TIER_MAPS.get(active, TIER_MODELS)
    if task_override:
        if task_override in tier_map:
            return tier_map[task_override]
        if task_override in TIER_ORDER:
            return tier_map[task_override]
        return task_override
    tier = worker_tier if worker_tier in TIER_ORDER else _DEFAULT_TIER
    if posture is None:
        posture = cost_posture(root)
    shift = _POSTURE_SHIFT.get(posture, 0)
    idx = max(0, min(len(TIER_ORDER) - 1, TIER_ORDER.index(tier) + shift))
    if min_tier and min_tier in TIER_ORDER:
        idx = max(idx, TIER_ORDER.index(min_tier))
    return tier_map[TIER_ORDER[idx]]


if __name__ == "__main__":
    import sys
    if "--display-name" in sys.argv:
        print(display_name())
    if "--pendo-subid" in sys.argv:
        print(pendo_config().get("subscription_id", ""))
    if "--databricks-catalog" in sys.argv:
        print(databricks_config().get("catalog", ""))
