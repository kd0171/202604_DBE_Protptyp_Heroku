# Prompt Test: Human Review Payload Update

## Changes

- Updated the Strategic Evidence Chunk prompt so that category, topic and strategic signal assignments must preserve the original source text supporting the assignment.
- Extended the final verification prompt so that it produces `human_review_payload_records` as the presentation-friendly final output of the prompt chain.
- Added a collapsible final output preview after the fourth prompt.
- The preview allows the user to paste the final JSON and renders the human-review-ready record as a table.

## Intended demo flow

1. Run the prompts manually in ChatGPT or another LLM interface.
2. Copy the final JSON output from Prompt 4.
3. Paste it into the final preview area.
4. The app displays the Human Review Payload as a table.

This output represents the structured data passed to Human Verification before verified records are saved to the database.
