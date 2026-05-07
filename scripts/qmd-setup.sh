#!/usr/bin/env bash
# qmd-setup.sh — Register all PM-OS collections in qmd
# Run this after a fresh install or if collections need to be recreated.
# Usage: bash scripts/qmd-setup.sh

set -e

QMD=/opt/homebrew/bin/qmd
PMDIR="$HOME/pm-os"

echo "Setting up QMD collections for PM-OS..."
echo

# Remove existing collections (safe to ignore errors)
for name in meetings_product meetings_leadership meetings_general meetings_strategy meetings_recruiting research product_artifacts tasks; do
  $QMD collection remove "$name" 2>/dev/null && echo "Removed existing: $name" || true
done

echo
echo "Adding collections..."

$QMD collection add "$PMDIR/datasets/meetings/product"    --mask "**/*.txt" --name meetings_product
$QMD collection add "$PMDIR/datasets/meetings/leadership" --mask "**/*.txt" --name meetings_leadership
$QMD collection add "$PMDIR/datasets/meetings/general"    --mask "**/*.txt" --name meetings_general
$QMD collection add "$PMDIR/datasets/meetings/strategy"   --mask "**/*.txt" --name meetings_strategy
$QMD collection add "$PMDIR/datasets/meetings/recruiting" --mask "**/*.txt" --name meetings_recruiting
$QMD collection add "$PMDIR/datasets/research/sources"    --mask "**/*.md"  --name research
$QMD collection add "$PMDIR/datasets/product"             --mask "**/*.md"  --name product_artifacts
$QMD collection add "$PMDIR/datasets/tasks"               --mask "**/*.md"  --name tasks

echo
echo "Adding context descriptions..."

$QMD context add qmd://meetings_product/    "Internal product team meeting transcripts by squad (home, payments, platform). Contains standups, planning, roadmap discussions, design reviews. Use for: product decisions, feature discussions, team signals, feature requests, pain points, integration gaps."
$QMD context add qmd://meetings_leadership/ "Leadership and cross-functional meeting transcripts. Contains strategy, org decisions, goal-setting, exec alignment. Use for: strategic direction, priorities, org context, and executive decisions."
$QMD context add qmd://meetings_general/    "General internal meeting transcripts (catch-ups, onboarding, cross-team syncs). Use for: relationship context, team dynamics, informal signals."
$QMD context add qmd://meetings_strategy/   "Strategy meeting transcripts. Contains company direction, OKR planning, and strategic initiative discussions."
$QMD context add qmd://meetings_recruiting/ "Recruiting and hiring meeting transcripts. Contains candidate interviews, hiring discussions, and team growth planning."
$QMD context add qmd://research/            "Strategic research library by topic: competitive-analysis, pricing-strategy, market-positioning, product-strategy, customer-segmentation, growth-strategy. Files have YAML frontmatter with expiry_date — check it for staleness."
$QMD context add qmd://product_artifacts/   "PM artifacts: PRDs, epics, backlog, roadmaps, strategies, customer briefs. PRDs have status flags (Drafting, Actionable, Closed, Abandoned). Use for: existing product decisions, feature specs, prioritization context."
$QMD context add qmd://tasks/               "Active task queues across human, agent, collab, and waiting queues. Each has YAML frontmatter: status, priority, domain, queue. Use for: current work-in-progress, pending decisions, open action items."

echo
echo "Done. Run 'qmd status' to verify."
echo "Next: run 'qmd embed' to build vector embeddings (~30-60min first run, requires ~2-4GB model download)."
