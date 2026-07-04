# Prompt Test General Prompt Revision and Human Review Table Fix

## Changes

- Removed preloaded ABF Annual Report source excerpts from the prompt text.
- Reworked all four Prompt Test prompts as general, reusable prompts with explicit input placeholders.
- Kept the Desired output column as an example of the expected JSON shape and final business output.
- Added more explicit extraction instructions for bioethanol plant closure events, including:
  - `company_name`
  - `business_unit`
  - `event_type`
  - `country`
  - `city_or_region`
  - `site_name`
  - `product_category`
  - `target_year`
  - `status`
  - `review_comment`
- Updated the final Human Review table preview to display only `human_review_payload_records` values from the pasted final JSON.
- Added a minimum height for the empty Human Review table preview so that an empty preview remains visible.

## Intended demo use

The prompts are designed to be copied into ChatGPT or another LLM interface. The presenter should paste relevant text from the Sample PDF manually. The page itself does not execute the prompts and does not embed source excerpts in the prompt text.
