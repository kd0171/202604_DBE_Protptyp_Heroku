# Analysis Workspace Update

## Purpose

The Data Analysis View was reorganized into one integrated analysis workspace. The page now contains a top-left switch between:

- Dashboard
- Interactive Mode

This avoids splitting the analytical story across several disconnected pages.

## Dashboard mode

The dashboard mode contains the following tabs:

1. Overview
2. Finance strength
3. Risk resilience
4. Sustainability maturity
5. Operational strength
6. Product portfolio
7. Regulatory readiness
8. Investment momentum

The overview tab provides the competitive radar, overall score ranking, score matrix, scoring logic, coverage and data gaps. Each axis tab provides detailed plots, generated interpretation text, weighted score details and evidence records.

## Scoring transparency

The scoring logic is shown in a collapsible weighting table in the overview tab. The table uses:

- `ci_axis_weights.csv`
- `ci_scoring_items.csv`
- `ci_weighted_score_details.csv`

The radar score therefore remains explainable and evidence-backed.

## Interactive Mode

The previous generic interactive mode was replaced with three competitive-intelligence questions:

1. Which competitor looks strongest overall and why?
2. Where is Nordzucker weakest compared with the competitors?
3. Which companies combine strong sustainability and operations?

The answers are prewritten in `interactive_queries.json` to simulate an LLM answer without requiring a live LLM API. The plots are computed from the scorecard CSVs, and the evidence table is filtered from `ci_extracted_indicators_long.csv`.

## Main modified files

- `app.py`
- `pages/analysis/competitive_scorecard.py`
- `pages/analysis/interactive_mode.py`
- `data/interactive_queries.json`
- `assets/style.css`
