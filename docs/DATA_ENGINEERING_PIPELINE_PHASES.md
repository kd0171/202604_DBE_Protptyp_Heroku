# Data Engineering Pipeline Phases

This document explains the phases shown in the Data Engineering View of the PoC application. The app uses a GitLab CI/CD-like visual style, but the phase names describe data-processing functions rather than software build, test, or deployment stages.

## Overview

The PDF is first processed by two common preprocessing phases. After the cleaned text is available, the flow splits into two branches:

```text
Source Intake
→ Text Preparation
→ split
   ├─ RAG Indexing
   │  → Retrieval Ready
   │
   └─ Event Extraction
      → Human Review & Validation
      → Structured Storage
```

The current PoC implements the frontend visualization, the animated pipeline and mock prompt/input/output details. It does not execute real PDF parsing, embedding generation, VectorDB storage, LLM API calls, backend jobs or database writes.

---

## 1. Source Intake

**Purpose:** Register the uploaded PDF as a stable source document.

This phase is common to both RAG and IE. It creates the basic source identity that all later chunks, extracted events and evidence snippets refer back to.

Typical jobs:

- `upload-pdf`: accepts the source PDF.
- `register-source`: creates a stable source record.
- `extract-metadata`: detects company name, document type, publication year and language.

**Output:** document/source metadata such as `document_id`, `source_id`, `company_name`, `document_type`, `publication_year`.

---

## 2. Text Preparation

**Purpose:** Convert the PDF into cleaned, machine-readable text.

This phase is also common to both branches. RAG and IE should not each parse the same PDF independently. Instead, both should reuse the same cleaned text and source references.

Typical jobs:

- `parse-pdf`: reads layout, pages and text blocks.
- `extract-clean-text`: removes repeated headers/footers and keeps page/section metadata.

**Output:** cleaned text blocks with stable source references such as page number, section and document ID.

---

## 3. RAG Indexing

**Purpose:** Prepare the document for retrieval-augmented generation.

This branch is retrieval-oriented. It does not primarily create structured event rows. Instead, it prepares the document so that a future chatbot or interactive dashboard can retrieve relevant passages.

Typical jobs:

- `chunk-document`: splits cleaned text into retrievable chunks.
- `create-embeddings`: conceptually converts chunks into vector representations.

**Output:** source-linked chunks and conceptual embedding artifacts.

---

## 4. Retrieval Ready

**Purpose:** Make indexed document content available for future RAG queries.

Typical jobs:

- `store-vector-db`: conceptually stores vectors and metadata in a Vector Database.
- `prepare-retrieval`: exposes the retrieval configuration to a future RAG backend.

**Output:** a retrieval-ready document collection, for example a conceptual `competitor_documents` VectorDB collection.

**PoC boundary:** This is shown conceptually only. The current app does not implement real embeddings, a VectorDB or live retrieval.

---

## 5. Event Extraction

**Purpose:** Extract structured competitor event candidates from the cleaned text.

This branch is IE-oriented. Its goal is not to answer a user question directly, but to transform text into structured data records.

Typical jobs:

- `select-passages`: selects text passages likely to contain relevant business events.
- `extract-events-json`: uses an IE prompt to produce JSON event candidates.
- `link-evidence`: attaches source evidence to each extracted event.

**Output:** event candidates such as company, event type, country, site, year, status, evidence text and confidence.

---

## 6. Human Review & Validation

**Purpose:** Complete validation through human confirmation.

Validation is not treated as finished immediately after the machine schema check. The automatic pre-check can identify missing fields or datatype problems, but the business correctness of an extracted event requires a human review step.

Typical jobs:

- `schema-precheck`: automatic technical check of JSON format, required fields and evidence availability.
- `human-review`: analyst approves, edits or rejects extracted event records based on evidence text.
- `validation-complete`: marks records as finally validated only after human review.

**Output:** human-validated event records with final `validation_status`.

---

## 7. Structured Storage

**Purpose:** Store human-validated events as analysis-ready structured data.

Only after human validation should event records be published to the relational event table used by dashboards and SQL-based analysis.

Typical jobs:

- `save-relational-db`: stores records in a relational event table.

**Output:** analysis-ready structured event records, for example `llm_extracted_company_events`.

---

## RAG vs IE: Conceptual Difference

| Branch | Main purpose | Main output |
|---|---|---|
| RAG | Retrieve relevant document passages and support grounded answers | Vector-indexed document chunks |
| IE | Extract facts/events from text and create structured data | Validated event table |

The two branches can share the same cleaned text. IE can also use retrieval-like passage selection to find relevant sections, but IE is still conceptually different from RAG because its output is structured data, not an answer generated for a user question.

---

## Implementation Boundary of the PoC

Implemented in the current app:

- Frontend upload UI
- Animated phase/job pipeline
- Clickable prompt, input, output and saved-artifact details
- Mock RAG and IE processing outputs
- Human Review UI and structured event table preview

Not implemented in the current app:

- Real PDF parsing
- Real LLM API calls
- Real embedding generation
- Real VectorDB storage
- Real RAG retrieval
- Backend job orchestration
- Relational database writes
- Authentication, audit logging and access control

---

## Human Validation Gate Behavior in the App

In the current frontend PoC, the animated pipeline intentionally stops at the `human-review` job inside **Human Review & Validation**.

Expected behavior:

1. The user uploads a PDF or starts the demo pipeline.
2. The automated jobs run until the IE branch reaches `human-review`.
3. `human-review` is shown with a yellow exclamation mark.
4. A warning message appears below the pipeline telling the user to check the extracted data.
5. The user opens the **Human Review** page.
6. After checking the extracted fields against the evidence text, the user clicks **Approve**.
7. The approval is stored in a browser session `dcc.Store`.
8. When the user returns to **Upload & Pipeline**, the Human Review & Validation gate changes to a green check mark.

This models the intended business rule: machine validation alone is not sufficient. The event data only becomes validated after human review.


### Return-to-pipeline behavior

The approval state is stored in a session-level `dcc.Store` in `app.py`, not inside the page-local pipeline state. This means that when the user returns from **Human Review** to **Upload & Pipeline**, the page-local animation state may be newly initialized, but the session approval flag is still available.

Therefore, once `Approve` has been clicked, the Upload & Pipeline page displays all jobs as green completed jobs for the current browser session. This prevents the pipeline from visually resetting to a white/pending state after navigation.
