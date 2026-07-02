# Business-grade plot explanation update

This update rewrites the plot explanation blocks in the Data Analysis View so that they follow a consistent analyst-oriented structure:

1. **How to read the plot** — explains the x-axis, y-axis, colours, score scale, bubble size, or heatmap cells.
2. **What it enables analytically** — explains which business question the plot is designed to answer.
3. **What the current data suggests** — summarises visible patterns and highlights concrete company-specific signals, especially Nordzucker as focal company and peer signals from Südzucker, Tereos, Pfeifer & Langen and ABF Sugar.

The explanatory text is intentionally prewritten in the prototype to simulate an LLM-generated interpretation. It is not generated dynamically from a live LLM API.

## Updated areas

- Strategic radar summary
- Latest operating-margin benchmark
- Overall strategic benchmark score
- Operating margin trend
- Revenue index trend
- Sugar-related segment margin trend
- EU white sugar price trend
- Profitability drawdown from recent peak
- Climate target comparison
- Operational emissions trend
- Operational footprint scatter
- Visible sugar production mix
- Product/co-product portfolio heatmap
- Product breadth indicator
- Reporting and policy readiness score
- EU market policy context
- Capex trend
- Investment intensity versus margin
- Interactive Mode related plot explanations

## Design rationale

The explanations avoid generic phrases such as “this chart shows...” and instead make clear how a Nordzucker analyst should use each plot in a strategic or operational discussion. The explanations also clarify important caveats, for example:

- radar charts are triage tools, not final conclusions;
- revenue trends must be interpreted with margins because sugar revenue can rise through price effects;
- group-level margins can hide sugar-segment stress;
- product breadth is not equal to product quality;
- disclosure readiness is not the same as low regulatory risk;
- capex must be classified by strategic intent before it is judged as positive or negative.
