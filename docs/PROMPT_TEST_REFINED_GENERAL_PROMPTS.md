# Prompt Test refined general prompts

Updated the Prompt Test prompts after testing showed that placeholder configuration fields produced weak missing-input outputs.

## Changes

- Removed bracket-style configuration placeholders such as `[FOCAL_COMPANY]` from prompt bodies.
- Kept the prompts general by not embedding ABF Annual Report source excerpts.
- Added a filled demo configuration for Nordzucker as focal company and ABF Sugar as peer scope.
- Preserved the requirement that users paste page-labelled source text from the Sample PDF into ChatGPT or another LLM.
- Made pipeline references lighter and more explanatory, while keeping coverage of:
  - Source Intake and Text Preparation
  - RAG branch evidence chunks
  - IE branch event and indicator extraction
  - Schema pre-check and Human Review payload
- Strengthened rules against creating placeholder, missing-data or pipeline-error events.
- Emphasized `extracted_text` as the original source passage used in Human Review.
