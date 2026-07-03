# Prompt Test View Update

This update adds a Prompt Test page at `/engineering/prompt-test`.

## Main changes

- Added a **Prompt Test** button below the Data Engineering button on the Home screen.
- Added a new Data Engineering subpage without PDF upload.
- The page keeps the same **Tutorial** and **Sample PDF** pattern as the Data Engineering View.
- The page displays four collapsible prompt-chain steps:
  1. Section and scope identification
  2. Strategic evidence chunk generation
  3. Event and indicator record extraction
  4. Evidence, schema and business logic verification
- Each prompt-chain item shows the prompt and the desired output side by side.
- Updated the Data Engineering pipeline wording so the pipeline is presented as LLM-assisted / prompt-configured rather than containing user-facing “No LLM prompt is used” checkpoints.

## Demo use

Use ABF Annual Report 2025. Copy relevant text from the ABF Sugar operating review and Financial Review segment table into ChatGPT or another LLM interface and run the prompts in order.
