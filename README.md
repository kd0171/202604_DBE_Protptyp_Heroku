# Competitive Intelligence Dashboard

This is a CSV-based Plotly Dash prototype for a Business Informatics lecture project.

## Core idea

The main function is not only a dashboard. The main function is a simulated LLM-based data engineering pipeline:

```text
Curated official/public documents
→ text extraction
→ prompt-based factual event extraction
→ JSON/schema validation
→ human review
→ structured event table
→ analytics dashboard and interactive exploration
```

## Views

### Data Engineering View

Shows the document-to-table pipeline:

1. Pipeline Overview
2. Upload & Register
3. LLM Extraction
4. Human Review
5. Save to Database

### Data Analysis View

Shows how the saved data can be used:

1. Market Overview
2. Regional Analysis
3. Event Analysis
4. Combined Interpretation
5. Interactive Mode

The Interactive Mode is a RAG-like interface. It does not use a real LLM, vector database or text-to-SQL. It maps natural-language-like questions to predefined intents in `interactive_queries.json`.

## Run

```bash
conda create -n nordzucker_data_product python=3.11 -y
conda activate nordzucker_data_product
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:8050/
```

## Important

All data is synthetic mock data. No real LLM call is executed.


## Navigation update

The root path `/` now shows a Home page. Clicking the application title in the top-left returns to Home.

Top-level navigation:

- Home
- Data Engineering View
- Data Analysis View

Each view has its own second-level navigation bar.


## Interaction update

Interactive Mode now uses English sample questions only, for example:

- What are recent competitor activities in Europe?
- Which competitor events are located in Germany?
- Summarize decarbonization and energy-efficiency activities
- Show bioethanol-related activities

The answer summaries are intentionally more detailed and mention relevant companies, countries and event types. They are still based on predefined mock data and do not call a live LLM.


## Human review update

The Human Review page now uses an editable DataTable. Edited visible rows can be saved into a Dash session store by clicking "Save edited table in session". This simulates a human-in-the-loop correction workflow without writing back to the CSV file.

## Interactive Mode update

Interactive Mode now uses more specific English questions and deeper answer summaries. The summaries mention companies, countries, event types, target years and source-grounded background. In a production system, all numeric values in these summaries should be generated from SQL/Text-to-SQL results rather than from free LLM generation.


## Reliability fix update

Human Review now uses explicit text input fields rather than direct DataTable editing.

Data flow:

1. Select event_id.
2. Populate input fields from dcc.Store.
3. Edit values in text fields.
4. Click Save selected event update.
5. Update the matching event_id record in dcc.Store.
6. Re-render the review table from dcc.Store.

Interactive Mode intent matching now selects the best-scoring intent rather than the first matching keyword. This fixes cases where broad words such as "competitor" captured a more specific question such as "Which bioethanol-related competitor activities were extracted?"


## Source text update

The source_text fields have been expanded so that each evidence snippet contains the information that is actually extracted into the event record, such as company, country, city/site, product category, target year and event type.

Interactive summaries have been rewritten as user-facing analysis text and no longer include phrases such as "in production" or "mock dataset" inside the generated summary.


## Redundant paraphrase column removed

Earlier versions included a column called `redundant natural-language paraphrase`. This was removed because it duplicated information already available in the structured fields and source_text.

The app now uses:

- source_text as the evidence snippet
- structured fields such as company_name, event_type, country, city, site_name, product_category and target_year as the extracted values

This makes the data model cleaner and avoids storing a second natural-language paraphrase of the same extraction.

## Interaction-gated engineering pages

Data Engineering pages now show key data only after the relevant user action:

- Upload & Register: source table appears after Register source
- LLM Extraction: snippets, JSON and extracted rows appear after Run simulated LLM extraction
- Save to Database: database preview appears after Save approved records to database


## Source Registration page clarification

The former Upload & Register page has been renamed and clarified as Document Source Registration.

Purpose:

- It does not perform LLM extraction.
- It registers which official/public document will be used as the source for extraction.
- It creates the metadata row that later extraction records reference through source_id.
- This makes the pipeline traceable and avoids uncontrolled document collection.
