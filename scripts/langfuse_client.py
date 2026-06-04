#!/usr/bin/env python3
"""
langfuse_client.py — Shared LangFuse SDK initialization for PM-OS.

Provides a single point of configuration for all LangFuse operations:
tracing, prompt management, scoring. Gracefully degrades when LangFuse
is unavailable or the package is not installed.

Configuration via environment variables:
  LANGFUSE_PUBLIC_KEY  — project public key
  LANGFUSE_SECRET_KEY  — project secret key
  LANGFUSE_HOST        — server URL (default: http://localhost:3000)

All public functions return None/no-op when LangFuse is not configured.
"""

import base64
import json
import os
import urllib.request

# ─── State ───────────────────────────────────────────────────────────────────

_langfuse = None
_enabled = None  # tri-state: None = not checked, True/False = cached


def _is_enabled():
    """Check if LangFuse is configured (has secret key) and importable."""
    global _enabled
    if _enabled is not None:
        return _enabled
    if not os.environ.get("LANGFUSE_SECRET_KEY"):
        _enabled = False
        return False
    try:
        import langfuse  # noqa: F401
        _enabled = True
    except ImportError:
        _enabled = False
    return _enabled


# ─── Core Client ─────────────────────────────────────────────────────────────

def get_langfuse():
    """Return a configured Langfuse client (singleton). Returns None if not available."""
    global _langfuse
    if not _is_enabled():
        return None
    if _langfuse is not None:
        return _langfuse
    from langfuse import Langfuse
    _langfuse = Langfuse(
        public_key=os.environ.get("LANGFUSE_PUBLIC_KEY", ""),
        secret_key=os.environ.get("LANGFUSE_SECRET_KEY", ""),
        host=os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
    )
    return _langfuse


def get_openai_client(base_url="http://localhost:11434/v1", api_key="ollama"):
    """Return an OpenAI client with LangFuse tracing. Falls back to plain openai."""
    if _is_enabled():
        from langfuse.openai import OpenAI
        return OpenAI(base_url=base_url, api_key=api_key)
    try:
        from openai import OpenAI
        return OpenAI(base_url=base_url, api_key=api_key)
    except ImportError:
        return None


# ─── Prompt Management ───────────────────────────────────────────────────────

def fetch_prompt(name, label="production", cache_ttl_seconds=300):
    """Fetch a prompt from LangFuse by name. Returns the prompt object or None."""
    lf = get_langfuse()
    if lf is None:
        return None
    try:
        return lf.get_prompt(name, label=label, cache_ttl_seconds=cache_ttl_seconds)
    except Exception:
        return None


# ─── REST API helpers ────────────────────────────────────────────────────────
# LangFuse v4 SDK changed its Python interface significantly. We use the REST
# API directly for trace creation and scoring — it's stable across versions.

def _rest_api(path, body):
    """POST to LangFuse REST API. Returns response dict or None."""
    if not _is_enabled():
        return None
    host = os.environ.get("LANGFUSE_HOST", "http://localhost:3000")
    pk = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    sk = os.environ.get("LANGFUSE_SECRET_KEY", "")
    auth = base64.b64encode(f"{pk}:{sk}".encode()).decode()

    data = json.dumps(body, default=str).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/api/public{path}",
        data=data,
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _rest_get(path, params=None):
    """GET the LangFuse public REST API. Returns parsed JSON or None."""
    if not _is_enabled():
        return None
    host = os.environ.get("LANGFUSE_HOST", "http://localhost:3000")
    pk = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    sk = os.environ.get("LANGFUSE_SECRET_KEY", "")
    auth = base64.b64encode(f"{pk}:{sk}".encode()).decode()
    url = f"{host}/api/public{path}"
    if params:
        import urllib.parse
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url += "?" + qs
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def list_scores(trace_ids=None, max_pages=20):
    """Return scores via the REST API, newest-first.

    The Python SDK's score read surface (`lf.api.score.list`) is broken on the
    installed LangFuse version (`'LangfuseAPI' object has no attribute 'score'`),
    so we read scores over REST — the same stable path used for writes. The
    /scores endpoint ignores a traceId query filter, so when `trace_ids` is given
    we page and filter client-side.

    Each score dict: {name, value, comment, traceId, dataType, timestamp}.
    """
    if not _is_enabled():
        return []
    want = set(trace_ids) if trace_ids is not None else None
    out = []
    page = 1
    while page <= max_pages:
        batch = _rest_get("/scores", {"limit": 100, "page": page})
        if not batch:
            break
        for s in batch.get("data", []):
            if want is None or s.get("traceId") in want:
                out.append(s)
        total_pages = batch.get("meta", {}).get("totalPages", page)
        if page >= total_pages:
            break
        page += 1
    return out


# ─── Tracing ─────────────────────────────────────────────────────────────────

def create_trace(name, session_id=None, metadata=None, tags=None, input_data=None, output_data=None):
    """Create a new trace via REST API. Returns trace dict with 'id' key, or None."""
    body = {"name": name}
    if session_id:
        body["sessionId"] = session_id
    if metadata:
        body["metadata"] = metadata
    if tags:
        body["tags"] = tags
    if input_data:
        body["input"] = input_data
    if output_data:
        body["output"] = output_data
    result = _rest_api("/traces", body)
    if result and "id" in result:
        result["_name"] = name  # stash for end_trace
    return result


def end_trace(trace, output=None, metadata=None, status_message=None, level=None):
    """Update a trace with completion data. No-op if trace is None."""
    if trace is None or "id" not in trace:
        return
    body = {"name": trace.get("_name", "trace")}  # name required for update
    if output is not None:
        body["output"] = output
    if metadata is not None:
        body["metadata"] = metadata
    if level is not None:
        body["level"] = level

    # Use the ingestion API to update the trace
    host = os.environ.get("LANGFUSE_HOST", "http://localhost:3000")
    pk = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    sk = os.environ.get("LANGFUSE_SECRET_KEY", "")
    auth = base64.b64encode(f"{pk}:{sk}".encode()).decode()

    # PATCH via ingestion batch endpoint
    import uuid
    event = {
        "id": str(uuid.uuid4()),
        "type": "trace-create",
        "timestamp": None,
        "body": {
            "id": trace["id"],
            **body,
        },
    }
    data = json.dumps({"batch": [event]}, default=str).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/api/public/ingestion",
        data=data,
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            pass
    except Exception:
        pass


# ─── Scoring ─────────────────────────────────────────────────────────────────

def score_trace(trace_id, name, value, comment=None, data_type="NUMERIC"):
    """Submit a score for a trace via REST API. No-op if LangFuse unavailable."""
    body = {
        "traceId": trace_id,
        "name": name,
        "value": value,
    }
    if comment:
        body["comment"] = comment
    if data_type:
        body["dataType"] = data_type
    return _rest_api("/scores", body)


# ─── Lifecycle ───────────────────────────────────────────────────────────────

def flush():
    """Flush pending events to LangFuse. Call at script exit."""
    lf = get_langfuse()
    if lf is not None:
        try:
            lf.flush()
        except Exception:
            pass


def shutdown():
    """Flush and shut down the client."""
    global _langfuse
    if _langfuse is not None:
        try:
            _langfuse.flush()
            _langfuse.shutdown()
        except Exception:
            pass
        _langfuse = None
