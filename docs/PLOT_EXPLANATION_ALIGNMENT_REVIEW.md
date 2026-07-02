# Plot explanation alignment review

This update verifies every plot description against the actual Plotly figure functions in `pages/analysis/competitive_scorecard.py`.

## Verification method

Each plot was checked against:

- Plot type (`line`, `bar`, `scatter`, `heatmap`, `scatterpolar`)
- Actual x-axis and y-axis title in the figure function
- Legend / colour encoding
- Size encoding for scatter plots
- Whether the data source is group-level, sugar-segment-level or curated score data
- Whether the current text claimed information not visible in the plot

## Issues found in the previous version

1. Several explanations were business-relevant but too generic and did not explicitly match the displayed x-axis and y-axis.
2. The production-mix explanation did not sufficiently warn that ABF Sugar has total capacity in the operations profile but no extracted beet/cane split, so it is not fully represented in the beet/cane production bars.
3. The climate-target explanation needed to clarify that values of 100 for net-zero or climate-neutrality are ambition markers, not comparable achieved percentage reductions.
4. The finance margin explanation needed to state that the finance trend mixes reporting bases: ABF is ABF Sugar segment data, while Südzucker and Tereos are group-level in `ci_financial_timeseries.csv` unless otherwise stated in hover data.
5. The capex explanation needed to state more clearly that values are in reported currencies and scopes, so absolute EUR/GBP values should not be compared without caution.
6. The investment-intensity explanation needed to state that only companies with capex, revenue and margin data appear in the plot.

## Fix implemented

All entries in `PLOT_EXPLANATIONS` were rewritten to use the following structure:

1. **How to read this plot**: actual plot type, x-axis, y-axis, legend/colour/size encoding.
2. **What this plot can analyse**: the business question the plot supports.
3. **What the current data suggests**: data-driven interpretation and Nordzucker-specific implication.

The updated explanations are now directly tied to the actual chart definitions and should be suitable for presentation and prototype review.
