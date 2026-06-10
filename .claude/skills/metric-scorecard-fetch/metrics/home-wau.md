---
slug: home-wau
source: auto
mcp: pendo
---
# Home WAU (web, 4-week rolling average)
This is the long-lived scorecard definition. It is intentionally independent of the
quarterly Rocks/OKR skill (which is temporal). Do NOT replace this with a reference to that skill.

Conventions: Pendo subId=4818486697721856; appId=5961191088521216 (Home WEB only — excludes the
native mobile apps); weeks are Sun 00:00 → Sat 23:59; all windows inclusive of as_of_date.

Call (single query, weekly buckets):
  activityQuery(subId=4818486697721856, appId=5961191088521216, entityType="visitor",
    group=["visitorId"], count=true, period="weekly",
    dateRange={range:"custom", startDate:<as_of-27d, the Sunday>, endDate:<as_of, the Saturday>})
Response returns exactly 4 weekly buckets in results[].rows[].count.
value = round(sum(4 bucket counts) / 4)   # integer unique visitors
raw = the 4 bucket counts (list).
Sanity: ~470–510k. Gotchas: must be exactly 4 weekly buckets (not 3/5); never use lastNDays
(it excludes today and breaks inclusivity); never widen to a 12-week/90-day window.

Return ONLY this JSON:
{"slug":"home-wau","value":<int|null>,"raw":<list>,"status":"ok|error|stale","notes":"<short>"}
