# Competitive Scorecard View

## Purpose

The `Competitive Scorecard` analysis page replaces placeholder analysis charts with an evidence-backed competitor scoring dashboard for Nordzucker AG and selected competitors.

The view is based on official PDFs in `documents/` plus clearly separated official website supplements for cases where a PDF was not available locally, especially ABF Sugar.

## Main data files

| File | Purpose |
|---|---|
| `data/ci_extracted_indicators_long.csv` | Long-form evidence table: company, axis, metric, value, source document/page and evidence text. |
| `data/ci_axis_scores.csv` | Final radar-score input table: company, axis, score, confidence, evidence IDs and rationale. |
| `data/ci_weighted_score_details.csv` | Detailed score calculation by company, axis and weighted scoring item. |
| `data/ci_scoring_items.csv` | Generic scoring rubric and item weights for each axis. |
| `data/ci_axis_weights.csv` | Axis-level weights used for the overall score. |
| `data/ci_overall_scores.csv` | Company-level overall scores derived from axis scores. |
| `data/ci_axis_coverage_summary.csv` | Evidence coverage and confidence per company and axis. |
| `data/ci_data_gaps_and_warnings.csv` | Known data limitations and comparability warnings. |

## Radar axes

The radar chart uses seven axes:

1. Finance strength
2. Risk resilience
3. Sustainability maturity
4. Operational strength
5. Product portfolio
6. Regulatory readiness
7. Investment momentum

Higher score is always better. For the risk axis, the score means **risk resilience / lower concern**, not higher risk severity.

## Scoring model

Each axis is scored on a 1 to 5 scale. The page shows a collapsible scoring logic table in the right-hand panel:

- Axis weights: all seven axes are currently equally weighted.
- Sub-item weights: each axis is composed of four weighted scoring items.
- Detailed scoring: `ci_weighted_score_details.csv` stores company-specific sub-scores, weighted contributions, evidence IDs and rationale.

The model is intentionally editable. If the group wants to emphasize strategy, sustainability or financial strength, only the CSV weights and sub-scores need to be adjusted.

## Page components

| Component | Description |
|---|---|
| Company selector | Select one or multiple companies for comparison. |
| Axis selector | Controls the ranking chart and evidence/detail tables. |
| KPI cards | Overall score and average evidence confidence. |
| Radar chart | Multi-company comparison across all seven axes. |
| Scoring logic panel | Collapsible table with axis and sub-item weights. |
| Selected axis ranking | Horizontal bar chart for the selected axis. |
| Score matrix | Heatmap-style overview of all companies and axes. |
| Weighted score detail table | Shows why each selected-axis score was assigned. |
| Evidence records table | Shows the extracted official-document evidence behind the selected axis. |
| Coverage and warnings | Shows evidence depth and known data gaps. |

## Implementation notes

- The page is implemented in `pages/analysis/competitive_scorecard.py`.
- It is now the first Data Analysis tab and the target of the top-level `Data Analysis View` navigation link.
- The scorecard uses Plotly `Scatterpolar` for the radar chart and CSV-backed Dash DataTables for transparency.
- Scores are rule-based and editable, not generated dynamically by an LLM at runtime.
