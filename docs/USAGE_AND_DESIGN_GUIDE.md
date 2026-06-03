# Usage and Design Guide

## 1. Intended user

The application is intended for a Nordzucker Strategy / Market Intelligence user who wants to understand competitor activities from public documents.

## 2. Application structure

The app is divided into two main views.

### Data Engineering View

This view demonstrates how public reports become structured data. It is the main conceptual function of the data product.

Use it to explain:

- which documents are selected
- how a prompt is applied
- what the extracted JSON looks like
- how humans review and correct the output
- how approved rows are saved to a normal database table

### Data Analysis View

This view demonstrates the value created by the structured data.

Use it to show:

- sugar market context
- regional production and trade structure
- company site footprint
- LLM-extracted competitor events
- combined regional activity
- natural-language-like exploration

## 3. Should Interactive Mode be a tab?

Yes. Interactive Mode should be a tab inside Data Analysis View, not inside Data Engineering View.

Reason:

- Data Engineering View is about creating reliable structured data.
- Interactive Mode is about consuming already saved data through a more user-friendly interface.
- It is an additional consumption layer, not part of the extraction pipeline itself.

## 4. RAG-like but not full RAG

The prototype does not implement embeddings, vector search or live LLM answers.

Instead:

- natural-language questions are matched to predefined intents
- each intent selects filters and charts
- values are computed from event tables
- evidence is shown through source_text
- summaries are prewritten or template-like

This gives a RAG-like user experience without implementing a full RAG architecture.

## 5. Hallucination prevention concept

In a production version:

- all numbers should come from SQL query results
- summaries should use allowed claims generated from database results
- every qualitative claim should link to event_id and source_text
- LLM validation can be used as an additional check, but not as the primary guarantee
- deterministic validation is required for counts, company names, countries and event types


## 6. Home page and navigation

The application root `/` displays a Home page rather than a Page not found error.

The Home page explains the two-view structure:

- Data Engineering View: creates structured event data from documents.
- Data Analysis View: consumes the saved data through dashboards and interactive exploration.

The application title in the top-left is clickable and returns the user to Home. This makes the prototype easier to present because the presenter can always return to the conceptual starting point.


## 7. Interactive Mode question language

Interactive Mode uses English example questions to make the demonstration more consistent for a Business Informatics presentation.

Example questions:

- What are recent competitor activities in Europe?
- Which competitor events are located in Germany?
- Summarize decarbonization and energy-efficiency activities
- Show bioethanol-related activities

The generated summaries mention companies and event categories explicitly, for example Südzucker, Pfeifer & Langen, Tereos and ABF Sugar. The summaries are still predefined and grounded in the mock event table.


## 8. Human review editability

The Human Review page is designed as a human-in-the-loop control point.

The user can edit visible rows in the review table and save the edited values into the current session. In the prototype this does not update the CSV file, but it demonstrates how the production system would allow analysts to correct extracted fields before database storage.

Typical editable fields:

- event_type
- country
- city
- site_name
- product_category
- target_year
- status
- validation_status
- human_verified
- review_comment

## 9. Interactive summaries and Text-to-SQL architecture

Interactive Mode now displays deeper summaries with company-level and country-level interpretation.

In production, however, the numeric values inside those summaries must not be generated freely by an LLM. Instead:

1. The user question is mapped to an intent.
2. The intent is translated into SQL or a predefined SQL template.
3. The database returns counts, companies, countries, event types and years.
4. The summary generator receives only those SQL-grounded results and linked source_text snippets.
5. A validation layer checks that claims in the generated summary match the database results.

A validation LLM may be used as an additional consistency checker, but it cannot replace deterministic SQL-based validation.


## 10. Reliable Human Review data flow

The Human Review page now avoids direct editable DataTable persistence because it can be unreliable for a presentation prototype.

Instead, it uses a deterministic form-based update flow:

```text
event_id dropdown
→ input fields populated from dcc.Store
→ analyst edits values
→ Save selected event update
→ matching event_id record updated in dcc.Store
→ review table re-rendered from dcc.Store
```

This mirrors a production approach where `event_id` is the primary key and updates are committed to a database transaction.

## 11. Interactive intent matching fix

Interactive Mode now selects the best matching intent by keyword score and exact example-question match.

This prevents broad intents from capturing specific questions. For example:

```text
Which bioethanol-related competitor activities were extracted?
```

should now select the Bioethanol-related activities intent rather than the general European competitor activity overview.


## 12. Removal of redundant paraphrase column

The `redundant natural-language paraphrase` field has been removed.

Reason:

- It was only a natural-language paraphrase of the structured fields.
- It did not add analytical value beyond `source_text` and the extracted columns.
- It could create confusion because users might treat it as a second source of truth.

The current design uses `source_text` as evidence and structured fields as the actual extraction result.

## 13. Action-based display in Data Engineering View

The engineering workflow now behaves more like an actual pipeline:

1. Source registration table appears after clicking Register source.
2. LLM extraction output appears after clicking Run simulated LLM extraction.
3. Database preview appears after clicking Save approved records to database.

This better communicates that each output is produced by a previous workflow step.
