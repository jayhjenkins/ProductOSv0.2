---
slug: mobile-wau
source: auto
mcp: pendo
---
# Mobile WAU (iOS + Android, 4-week rolling average)
Long-lived, self-contained scorecard definition. subId=4818486697721856.

Same 4-week methodology as home-wau, but summed across BOTH native mobile appIds:
  5355360917585920 and 6607066993197056.
For EACH appId, run:
  activityQuery(subId=4818486697721856, appId=<that one>, entityType="visitor",
    group=["visitorId"], count=true, period="weekly",
    dateRange={range:"custom", startDate:<as_of-27d>, endDate:<as_of>})
Average that app's 4 weekly buckets, then ADD the two app averages.
value = round(app1_4wkavg + app2_4wkavg). raw = {"app1": app1_4wkavg, "app2": app2_4wkavg}.
Sanity: ~10–20k. These are separate native apps; cross-app overlap is negligible, so summing
is acceptable (we intentionally do NOT attempt cross-app dedupe).

Return ONLY this JSON:
{"slug":"mobile-wau","value":<int|null>,"raw":<obj>,"status":"ok|error|stale","notes":"<short>"}
