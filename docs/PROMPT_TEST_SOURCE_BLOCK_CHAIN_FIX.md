# Prompt Test source-block chain fix

Updated the Prompt Test prompts so Prompt 1 now carries forward exact source blocks in `prepared_source_blocks[].original_text`.

Reason: Prompt 2 previously expected `SOURCE_TEXT`, but users naturally pasted the JSON output from Prompt 1. Because Prompt 1 only contained section metadata and not the original source passage, Prompt 2 correctly returned `missing_input`.

New design:

1. Prompt 1: Source Intake + Text Preparation, including reusable verbatim `prepared_source_blocks`.
2. Prompt 2: Strategic evidence chunking from `prepared_source_blocks[].original_text`.
3. Prompt 3: Event and indicator extraction from chunks.
4. Prompt 4: Human Review payload with `extracted_text` evidence.

No ABF Annual Report source excerpts are embedded in the prompts. Desired outputs remain illustrative output-format examples only.
