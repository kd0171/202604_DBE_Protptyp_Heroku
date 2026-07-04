# Prompt Test pipeline-chain and extracted text update

This update revises the Prompt Test page so the four manual prompts explicitly map to the Data Engineering pipeline stages while remaining general prompts without embedded ABF Annual Report source excerpts.

## Changes

- Rewrote the four Prompt Test prompts as a compressed demo of the full pipeline:
  1. Source Intake + Text Preparation: `upload-pdf`, `register-source`, `extract-metadata`, `parse-pdf`, `extract-clean-text`
  2. RAG branch: `chunk-document`, `create-embeddings`, `store-vector-db`, `prepare-retrieval`
  3. IE branch: `select-passages`, `extract-events-json`, `link-evidence`
  4. Human Review & Validation: `schema-precheck`, `human-review`
- Kept prompts general and source-free. They require the presenter to paste relevant PDF text into the prompt input area.
- Kept ABF/Vivergo material only as desired-output format examples, not as embedded prompt input.
- Added `extracted_text` to strategic chunks, event records and final `human_review_payload_records` so the Human Review table contains the original source passage used for verification.
- Updated the Human Review table preview to include an `Extracted text / evidence` column.
- Adjusted the empty preview table to keep a visible minimum height.

## Rationale

The Prompt Test page now better represents the app pipeline as a staged LLM-assisted workflow: source registration and text preparation, retrieval-oriented strategic evidence chunking, IE event extraction with evidence links, and final schema pre-check before human verification.
