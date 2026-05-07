---
description: Unified semantic search across all PM-OS datasets (meetings, research, product artifacts, tasks)
---

Use the `context-search` skill to search for: $ARGUMENTS

Arguments format: `<query> [--collection <name>] [--mode semantic|keyword|hybrid]`

Examples:
- `/search payments onboarding friction` — hybrid search across all datasets
- `/search "resident portal pain points" --collection meetings_product` — product meetings only
- `/search competitive pricing --collection research --mode semantic` — semantic search in research
- `/search open tasks for home squad --collection tasks` — task search
