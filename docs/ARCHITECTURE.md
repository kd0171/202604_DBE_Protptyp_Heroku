# Architecture Explanation

## Main pipeline

```text
Document upload
→ source registration
→ text extraction
→ prompt application
→ event JSON
→ validation and normalization
→ human review
→ relational event table
```

## Data Engineering Layer

This layer creates structured data from unstructured public documents.

Tables:

- document_sources.csv
- llm_extracted_company_events.csv
- pipeline_steps.csv

## Data Analysis Layer

This layer consumes structured data.

Tables:

- market_indicators.csv
- country_sugar_stats.csv
- company_sites.csv
- llm_extracted_company_events.csv

## RAG-like Interaction Layer

This layer sits on top of the structured event database.

It maps a question such as:

```text
他企業のヨーロッパでの近年の動向を教えて
```

to:

```text
exclude_company = NORDZUCKER
event_presence = yes
```

and returns:

- a source-grounded answer summary
- related charts
- evidence table
- validation explanation

## Vector database position

A vector database is not required for this prototype.

It would only be needed in a production extension if users need semantic search across full report text, including text that was not already extracted into the event table.

The relational database remains the source of truth for counts, charts and structured facts.


## Summary generation and hallucination prevention

Interactive summaries should be generated from database results, not from the model's free-form knowledge.

Recommended production flow:

```text
User question
→ intent detection
→ Text-to-SQL or predefined SQL query template
→ SQL result table
→ source_text retrieval by event_id / chunk_id
→ answer generation from allowed claims
→ deterministic validation
→ optional LLM consistency validation
→ UI rendering
```

The relational database is the source of truth for:

- event counts
- company counts
- country lists
- event types
- target years
- investment amounts, if available

The LLM may help turn SQL-grounded results into readable language, but it should not invent numbers or company events.
