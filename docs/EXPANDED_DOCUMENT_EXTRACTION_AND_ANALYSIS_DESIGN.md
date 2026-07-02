# Expanded document extraction and redesigned analysis view

## Context

The `documents/` folder now contains expanded official PDFs and EU sugar market files. The analysis view was redesigned so that the detailed tabs are no longer only explanations of radar-chart scores. Instead, each tab uses analysis-specific plots that answer a business question relevant to Nordzucker as the focal company.

Nordzucker is treated as the focal company. Südzucker, Pfeifer & Langen, Tereos and ABF Sugar are treated as peer competitors.

## New extracted CSV files

| File | Purpose |
|---|---|
| `ci_document_inventory.csv` | Inventory of PDFs and market files in `documents/`, including company mapping and pages/sheets. |
| `ci_financial_timeseries.csv` | Group or company-level revenue, EBITDA, operating result, margins, capex, debt and employees where available. |
| `ci_segment_financial_timeseries.csv` | Sugar-related segment financials for direct comparability with Nordzucker. |
| `ci_operations_profile.csv` | Countries, plants, employees, production and raw-material notes. |
| `ci_product_portfolio_matrix.csv` | Binary product/co-product portfolio matrix for product diversification plots. |
| `ci_sustainability_targets.csv` | Climate and sustainability target records by company and scope. |
| `ci_emissions_timeseries.csv` | Nordzucker Scope 1 emissions time series from the transparency report. |
| `ci_market_price_timeseries.csv` | EU white sugar price trend extracted from EU market documents. |
| `ci_investment_events.csv` | Capex, restructuring, divestment and decarbonisation investment events. |
| `ci_regulation_context.csv` | Reporting readiness and regulatory context records. |
| `ci_analysis_plot_catalog.csv` | Explanation of the redesigned plots and why each plot matters. |
| `ci_extracted_indicators_long.csv` | Rebuilt long-format evidence table from the expanded extraction. |

## Redesigned tab logic

### Overview
The overview keeps the radar scorecard as a summary layer, but adds latest profitability, scoring logic, data gaps and the plot catalog. This prevents the radar from becoming the whole analysis.

### Finance
Finance now focuses on operating margin trend, indexed revenue trend and sugar-related segment margin trend. These plots are more meaningful than score evidence because they show whether profitability weakness is temporary or structural.

### Risk
Risk connects company performance with the EU sugar price downturn. The key plots are EU white sugar price trend and profitability drawdown from recent peak.

### Sustainability
Sustainability separates target ambition from operational proof. It includes climate-target comparison and Nordzucker Scope 1 emissions trend.

### Operations
Operations focuses on footprint, scale and raw-material exposure. It includes country-vs-plant footprint and visible production mix.

### Products
Products focuses on diversification beyond standard sugar. It includes product/co-product heatmap and product breadth indicator.

### Regulation
Regulation separates reporting readiness from policy exposure. It includes reporting/policy readiness score and EU sugar-price context.

### Investment
Investment focuses on capex trend, investment intensity and strategic events such as restructuring, divestment and energy-transition projects.

## Interactive Mode update

Interactive Mode now uses three Nordzucker-focused questions:

1. How has Nordzucker’s financial performance changed compared with peer competitors?
2. Which market risks should Nordzucker watch most closely?
3. Which peers combine sustainability ambition with visible investment activity?

Each answer is prewritten to simulate an LLM response grounded in the extracted CSV files. Each answer also displays a related plot and evidence table.

## Important limitations

- ABF Sugar PDFs were still not present in the local `documents/` folder. ABF Sugar values are official-web supplements and are flagged accordingly.
- Pfeifer & Langen financial data is limited to revenue and headline figures from the sustainability report. No EBIT/EBITDA/net debt was available in the uploaded documents.
- Group-level and sugar-segment data are not always directly comparable. The Finance tab therefore separates group financial trends from sugar-related segment trends.
