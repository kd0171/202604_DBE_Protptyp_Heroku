# Prompt Test: less leading demo instructions

Updated the Prompt Test guidance so that the prompt chain remains general and does not pre-label the ABF demo input as a specific event.

Changes:
- Removed explicit instruction to use named ABF sections or a Vivergo closure passage from the prompt input area.
- Replaced it with neutral guidance to paste concise, page-labelled source text containing concrete business facts.
- Replaced high-priority ABF-specific targets with general candidate information types such as financial performance, operational changes, closures, regulatory exposure, investment and sustainability projects.
- Updated tutorial and page copy to avoid over-directing the model before extraction.

The Desired output examples can still illustrate an ABF/Vivergo-style Human Review payload, but the executable prompts themselves remain general and require source evidence from the pasted text.
