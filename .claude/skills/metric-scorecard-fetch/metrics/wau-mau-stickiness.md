---
slug: wau-mau-stickiness
source: auto
mcp: pendo
---
# WAU/MAU Stickiness (web) — the weekly-to-monthly ratio
Long-lived, self-contained scorecard definition. subId=4818486697721856; appId=5961191088521216 (web).
Measures how many monthly users return weekly — the monthly→weekly conversion.

Two activityQuery calls (entityType="visitor", group=["visitorId"], count=true, period="dayRange"):
  WAU_week = dateRange={range:"custom", startDate:<as_of-6d>,  endDate:<as_of>}  → 1-week unique visitors
  MAU_30d  = dateRange={range:"custom", startDate:<as_of-29d>, endDate:<as_of>}  → 30-day unique visitors
value = round(WAU_week / MAU_30d, 4)   # decimal, e.g. 0.3201
raw = {"wau_week": WAU_week, "mau_30d": MAU_30d}. Sanity: 0.25–0.40.
Note: this WAU_week is the single most-recent week's uniques (NOT the 4-week average used by
the home-wau metric). Windows inclusive of as_of.

Return ONLY this JSON:
{"slug":"wau-mau-stickiness","value":<float|null>,"raw":<obj>,"status":"ok|error|stale","notes":"<short>"}
