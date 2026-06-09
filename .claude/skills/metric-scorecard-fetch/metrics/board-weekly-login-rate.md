---
slug: board-weekly-login-rate
source: auto
mcp: pendo
---
# Board Member Weekly Login Rate
Long-lived scorecard definition; intentionally independent of the quarterly Rocks/OKR skill.
Do NOT replace with a reference to that skill.

Conventions: Pendo subId=4818486697721856; appId=5961191088521216 (Home web);
segment "Home | Board Members" segmentId="ruTWzJHTx86HCgbOfdAP80T85UQ" (canonical board-member
definition — always use the segmentId, not a metadata.isboardmember filter); windows inclusive of as_of.

Two calls (entityType="visitor", group=["visitorId"], count=true, segmentId as above, period="dayRange"):
  num7d  = activityQuery(... dateRange={range:"custom", startDate:<as_of-6d>,  endDate:<as_of>})
  num90d = activityQuery(... dateRange={range:"custom", startDate:<as_of-89d>, endDate:<as_of>})
value = round(num7d / num90d, 4)   # decimal, e.g. 0.3146
raw = {"n7": num7d, "n90": num90d}. Sanity: 0.28–0.40.

Return ONLY this JSON:
{"slug":"board-weekly-login-rate","value":<float|null>,"raw":<obj>,"status":"ok|error|stale","notes":"<short>"}
