---
slug: home-tickets-per-1k-wau
source: auto
mcp: databricks
depends_on: home-wau
---
# New Home Tickets per 1,000 WAU
Long-lived, self-contained scorecard definition. Databricks is_prod only, READ-ONLY.

Count Home tickets created in the trailing 7 days inclusive of as_of:
  SELECT COUNT(*) AS c FROM is_prod.zendesk.ticket
  WHERE custom_product_field = 'home__'
    AND created_at >= DATE_SUB(DATE('<as_of>'), 6)
    AND created_at <  DATE_ADD(DATE('<as_of>'), 1)
raw = that count (e.g. 73).
value = round(count / (home_wau / 1000), 2)   # uses THIS week's home-wau value passed to you
Caveat to record in notes: most tickets are untagged (NULL product field), so this is a
tagging-dependent floor, not a complete Home ticket count. Sanity: raw ~50–120, rate ~0.10–0.30.

Return ONLY this JSON:
{"slug":"home-tickets-per-1k-wau","value":<float|null>,"raw":<int>,"status":"ok|error|stale","notes":"<short>"}
