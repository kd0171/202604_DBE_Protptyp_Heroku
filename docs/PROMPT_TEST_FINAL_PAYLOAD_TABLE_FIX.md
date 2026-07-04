# Prompt Test final payload and table preview update

## Changes

- Rewrote the Prompt Test chain so the copied prompts are self-contained for the presentation demo.
- Added ABF Annual Report 2025 demo excerpts directly inside the prompts to avoid weak placeholder outputs such as missing-source-text records.
- Strengthened the prompt chain around five meaningful ABF Sugar review records:
  - finance/risk: Sugar profitability deterioration
  - operations/risk/investment: Azucarera restructuring
  - regulation/risk/operations: Vivergo closure
  - investment/operations: Ubombo capacity expansion
  - sustainability/investment/operations: British Sugar decarbonisation projects
- Strategic evidence chunks now preserve original source text for topic, category and strategic signal assignments.
- Prompt 4 now explicitly generates `human_review_payload_records` as the final presentation output.
- Human Review table preview now renders only values from the final JSON field `human_review_payload_records`.
- Empty or invalid final JSON input shows only an empty preview table with a few blank rows.
- Removed fallback behaviour that previously rendered `event_records` or placeholder/error records as the final table.

## Note

The prompts remain a demonstrative prompt-chain design for the prototype. They are intended to show the logic of a robust LLM-assisted workflow, not to claim that the deployed prototype executes a live LLM backend.
