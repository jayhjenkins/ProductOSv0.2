---
slug: rage-click-rate
source: auto
mcp: pendo
depends_on: home-wau
---
# Home Rage-Click Rate per 1,000 WAU
Long-lived, self-contained scorecard definition. subId=4818486697721856; appId=5961191088521216 (web).

One call:
  activityQuery(subId=4818486697721856, appId=5961191088521216, entityType="page",
    group=["pageId"], count=false, frustrationMetrics=true, period="dayRange",
    dateRange={range:"custom", startDate:<as_of-6d>, endDate:<as_of>}, limit=1000)
total_rage = sum of rageClickCount across ALL returned page rows (includes the Pre-Login page).
value = round(total_rage / (home_wau / 1000), 1)   # uses THIS week's home-wau value passed to you
raw = total_rage. Sanity: ~10–60. Windows inclusive of as_of.

Return ONLY this JSON:
{"slug":"rage-click-rate","value":<float|null>,"raw":<int>,"status":"ok|error|stale","notes":"<short>"}
