from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import dash
from dash import ALL, Input, Output, State, callback, ctx, dcc, html
import dash_bootstrap_components as dbc

from utils import LLM_EVENT_COLUMNS, compact_table, data_note, load_data


dash.register_page(__name__, path="/engineering/upload-pipeline", name="Upload & Pipeline")

DEFAULT_FILE = "abf-annual-report-2025.pdf.downloadasset.pdf"
SUPPORTED_SAMPLE_PREFIXES = ("abf-annual-report-2025", "abf annual report 2025")
APP_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PDF_CANDIDATES = [
    APP_ROOT / "assets" / "compressed_documents" / "04_abf-sugar" / DEFAULT_FILE,
    APP_ROOT / "assets" / "comp" / "04_ABF" / DEFAULT_FILE,
    APP_ROOT / "documents" / "04_abf-sugar" / DEFAULT_FILE,
]
SAMPLE_PDF_PATH = next((path for path in SAMPLE_PDF_CANDIDATES if path.exists()), SAMPLE_PDF_CANDIDATES[0])
ENGINEERING_SAMPLE_EVENTS_PATH = APP_ROOT / "data" / "engineering_sample_events.csv"

data = load_data()
events = pd.read_csv(ENGINEERING_SAMPLE_EVENTS_PATH) if ENGINEERING_SAMPLE_EVENTS_PATH.exists() else data["events"].copy()
if "event_id" in events.columns:
    events = events[events["event_id"].astype(str).ne("event_id")]

EVENT_FIELDS = [
    "event_id", "company_name", "event_type", "country", "city", "site_name",
    "product_category", "target_year", "status", "source_text",
    "extraction_confidence", "validation_status", "human_verified", "review_comment",
]

FINAL_TABLE_COLUMNS = [
    "event_id", "company_name", "event_type", "country", "city", "site_name",
    "product_category", "target_year", "status", "source_document_title", "source_page", "source_link",
    "extraction_confidence", "validation_status", "human_verified", "review_comment",
]

PHASE_LABELS = {
    "source_intake": "Source Intake",
    "text_preparation": "Text Preparation",
    "rag_indexing": "RAG Indexing",
    "retrieval_ready": "Retrieval Ready",
    "event_extraction": "Event Extraction",
    "human_validation": "Human Review & Validation",
    "structured_storage": "Structured Storage",
}

COMMON_PHASES = ["source_intake", "text_preparation"]
RAG_PHASES = ["rag_indexing", "retrieval_ready"]
IE_PHASES = ["event_extraction", "human_validation", "structured_storage"]

LLM_PROMPT_STEPS = {
    "metadata_extraction",
    "select_passages",
    "extract_events_json",
    "link_evidence",
}

JOBS = [
    {
        "key": "upload_pdf",
        "phase": "source_intake",
        "name": "upload-pdf",
        "short": "Upload official PDF",
        "purpose": "Accept a competitor PDF as the raw source document for both the RAG and IE branches.",
        "semantic": False,
        "prompt": "No LLM prompt is used in this step.",
        "input": "User-selected PDF file from the upload component.",
        "output": {
            "document_id": "doc_demo_2025_001",
            "file_name": DEFAULT_FILE,
            "source_type": "annual_report",
            "status": "uploaded",
        },
        "saved": "document_registry / document_id=doc_demo_2025_001",
        "note": "In a production system this step would store the raw PDF in object storage and create an immutable document identifier. In this frontend PoC, only the filename and mocked metadata are shown.",
    },
    {
        "key": "register_source",
        "phase": "source_intake",
        "name": "register-source",
        "short": "Create source record",
        "purpose": "Create a stable source record so later chunks, extracted events and evidence snippets can be traced back to the same PDF.",
        "semantic": False,
        "prompt": "No LLM prompt is used in this step.",
        "input": "Uploaded PDF and analyst-selected source category.",
        "output": {
            "source_id": "SRC_DEMO_NZ_2025",
            "document_id": "doc_demo_2025_001",
            "source_owner": "Nordzucker",
            "human_selected": True,
        },
        "saved": "document_sources table",
        "note": "This step is important for traceability. Every RAG chunk and IE event should keep the source_id so the dashboard can point back to the document.",
    },
    {
        "key": "metadata_extraction",
        "phase": "source_intake",
        "name": "extract-metadata",
        "short": "Detect company and document metadata",
        "purpose": "Create document-level metadata before indexing and event extraction.",
        "semantic": True,
        "prompt": "Extract document-level metadata: company name, document title, publication year, language, source type and reporting period. Return only valid JSON.",
        "input": "First pages, filename, detected title area and PDF metadata fields.",
        "output": {
            "company_name": "Nordzucker AG",
            "document_title": "Annual Report 2025",
            "publication_year": 2025,
            "language": "en",
            "document_type": "annual_report",
        },
        "saved": "document_metadata table",
        "note": "This is a semantic step if an LLM is used to interpret title pages or reporting context. The PoC displays the prompt and mocked JSON output.",
    },
    {
        "key": "parse_pdf",
        "phase": "text_preparation",
        "name": "parse-pdf",
        "short": "Parse PDF layout",
        "purpose": "Prepare the uploaded PDF for downstream text-based processing.",
        "semantic": False,
        "prompt": "No LLM prompt is used in this step.",
        "input": "PDF binary content.",
        "output": {
            "pages_processed": 112,
            "layout_blocks": 418,
            "page_reference_mode": "page_number + block_id",
        },
        "saved": "parsed_pdf_blocks table / document_layout.jsonl",
        "note": "Implementation still has to be decided. A production version could use a PDF parser such as PyMuPDF, pdfplumber or an OCR pipeline if scanned pages are present.",
    },
    {
        "key": "extract_clean_text",
        "phase": "text_preparation",
        "name": "extract-clean-text",
        "short": "Extract and clean machine-readable text",
        "purpose": "Create a cleaned text representation that can be reused by both RAG indexing and IE extraction.",
        "semantic": False,
        "prompt": "No LLM prompt is required by default. Cleaning can be rule-based; an LLM could optionally be used for difficult section normalization.",
        "input": "Parsed PDF blocks with page and layout metadata.",
        "output": {
            "text_blocks": 376,
            "cleaned": True,
            "metadata_fields": ["document_id", "page", "section", "company", "year"],
        },
        "saved": "cleaned_text_blocks table / cleaned_document.jsonl",
        "note": "The key user-facing point is that page and section references must not be lost. Both RAG answers and IE evidence depend on these references.",
    },
    {
        "key": "chunk_document",
        "phase": "rag_indexing",
        "name": "chunk-document",
        "short": "Split document into retrieval chunks",
        "purpose": "Prepare text for future RAG retrieval by splitting it into stable, source-linked chunks.",
        "semantic": False,
        "prompt": "No LLM prompt is required. Rule-based chunking by section, page and token length is sufficient for the PoC concept.",
        "input": "Cleaned text blocks with source references.",
        "output": {
            "chunks_created": 137,
            "average_chunk_tokens": 430,
            "metadata_attached": True,
        },
        "saved": "rag_chunks collection",
        "note": "This step belongs to the RAG branch. Its output is not a business event table, but retrieval units for a future chatbot or grounded answer system.",
    },
    {
        "key": "create_embeddings",
        "phase": "rag_indexing",
        "name": "create-embeddings",
        "short": "Create vector representations",
        "purpose": "Show where embeddings would be generated for the document chunks.",
        "semantic": False,
        "prompt": "No LLM generation prompt is used. An embedding model would convert chunks into vectors.",
        "input": "Cleaned chunks and metadata.",
        "output": {
            "vectors_created": 137,
            "embedding_model": "conceptual placeholder in frontend PoC",
            "dimension": "not executed",
        },
        "saved": "embedding batch artifact",
        "note": "Implementation is deliberately left as a future backend task. The PoC only shows the expected artifact and where it would belong in the architecture.",
    },
    {
        "key": "store_vector_db",
        "phase": "retrieval_ready",
        "name": "store-vector-db",
        "short": "Store chunks in Vector DB",
        "purpose": "Show where chunks and vectors would be stored for future retrieval-augmented queries.",
        "semantic": False,
        "prompt": "No LLM prompt is used. Vector DB storage is a data infrastructure step.",
        "input": "Chunk texts, embeddings and document metadata.",
        "output": {
            "collection": "competitor_documents",
            "upserted_vectors": 137,
            "retrieval_ready": True,
        },
        "saved": "VectorDB collection: competitor_documents",
        "note": "The current app does not implement a VectorDB. This card communicates that the RAG branch would become queryable from this point onward.",
    },
    {
        "key": "prepare_retrieval",
        "phase": "retrieval_ready",
        "name": "prepare-retrieval",
        "short": "Expose retrieval index to the interactive layer",
        "purpose": "Make the indexed document available for a future RAG-based chatbot or interactive dashboard.",
        "semantic": False,
        "prompt": "No answer-generation prompt is executed in the frontend PoC. In production, the query would be embedded, relevant chunks retrieved and passed to an LLM.",
        "input": "Vector DB collection and retrieval metadata.",
        "output": {
            "rag_query_ready": True,
            "future_frontend": "Interactive Dashboard / Chatbot",
            "implemented_now": "RAG-like static interaction only",
        },
        "saved": "retrieval_config / collection alias",
        "note": "This is the handover point from Data Engineering to a future RAG backend. The current Data Analysis View remains mock-data based.",
    },
    {
        "key": "select_passages",
        "phase": "event_extraction",
        "name": "select-passages",
        "short": "Select passages relevant for event extraction",
        "purpose": "Identify text sections likely to contain competitor events. This can be rule-based, retrieval-assisted or prompt-based.",
        "semantic": True,
        "prompt": "Select passages that mention investments, capacity changes, plant modernization, closures, decarbonization, partnerships, market entries or product expansion. Keep page and source references.",
        "input": "Cleaned text blocks, optionally supported by retrieval over chunks.",
        "output": {
            "candidate_passages": 28,
            "pages_covered": 14,
            "event_keywords_detected": ["investment", "capacity", "energy efficiency"],
        },
        "saved": "ie_candidate_passages table",
        "note": "This is part of the IE branch. It narrows the document before structured extraction so the event prompt does not process irrelevant text.",
    },
    {
        "key": "extract_events_json",
        "phase": "event_extraction",
        "name": "extract-events-json",
        "short": "Extract competitor business events",
        "purpose": "Use an IE prompt to convert relevant document passages into structured event candidates.",
        "semantic": True,
        "prompt": "You are an information extraction assistant for competitive intelligence. Extract only explicit events related to investments, plant closures, capacity changes, decarbonization, partnerships, product expansion and market entries. For each event, return company_name, event_type, country, city, site_name, product_category, target_year, status, evidence_text and confidence. Do not infer facts not supported by the text.",
        "input": "Selected passages from the cleaned document.",
        "output": [
            {
                "event_id": "evt_001",
                "company_name": "British Sugar",
                "event_type": "decarbonization_project",
                "country": "United Kingdom",
                "site_name": "Wissington",
                "target_year": 2026,
                "confidence": 0.86,
            },
            {
                "event_id": "evt_002",
                "company_name": "Südzucker",
                "event_type": "capacity_adjustment",
                "country": "Germany",
                "site_name": "Offstein",
                "target_year": 2025,
                "confidence": 0.78,
            },
        ],
        "saved": "events_pending_extraction.json",
        "note": "This is the central LLM-based Information Extraction step. Its result is not a final answer, but draft structured event data that still needs validation.",
    },
    {
        "key": "link_evidence",
        "phase": "event_extraction",
        "name": "link-evidence",
        "short": "Attach source evidence",
        "purpose": "Ensure that every extracted event can be traced back to a page, section and source text fragment.",
        "semantic": True,
        "prompt": "For each extracted event, quote the shortest source passage that directly supports the event. Return event_id, page, section, evidence_text and evidence_strength.",
        "input": "Event candidates and source passages.",
        "output": {
            "events_with_evidence": 5,
            "missing_evidence": 0,
            "evidence_fields": ["page", "section", "source_text"],
        },
        "saved": "event_evidence table",
        "note": "This step makes the IE output auditable. The Human Review panel uses this evidence text to let the analyst confirm or correct the extracted data.",
    },
    {
        "key": "schema_precheck",
        "phase": "human_validation",
        "name": "schema-precheck",
        "short": "Automatic schema pre-check",
        "purpose": "Run an automatic technical pre-check before analyst review. This checks whether JSON can be reviewed, not whether the business content is final.",
        "semantic": False,
        "prompt": "No LLM prompt is required. JSON schema validation checks required fields, data types, controlled vocabularies and evidence availability.",
        "input": "Extracted event JSON records with linked evidence text.",
        "output": {
            "records_checked": 5,
            "machine_check_passed": 4,
            "requires_human_review": 5,
        },
        "saved": "machine_validation_report.json",
        "note": "This step can be automatic, but it does not complete validation. The pipeline intentionally stops at human-review after this pre-check.",
    },
    {
        "key": "human_review",
        "phase": "human_validation",
        "name": "human-review",
        "short": "Analyst confirms or corrects extracted events",
        "purpose": "The human reviewer checks extracted event values against the evidence text. Only after this review can the validation be treated as completed.",
        "semantic": False,
        "prompt": "No generation prompt is executed here. The analyst approves, edits or rejects each record based on source evidence.",
        "input": "Event candidates, evidence text, confidence values and automatic schema pre-check results.",
        "output": {
            "review_status": "waiting_for_human_approval",
            "pipeline_gate": "blocked",
        },
        "saved": "human_review_decisions table",
        "note": "This is the only required manual interaction in the PoC. The pipeline shows a yellow exclamation mark here until the Approve button is clicked.",
    },
    {
        "key": "validation_complete",
        "phase": "human_validation",
        "name": "validation-complete",
        "short": "Mark records as validated",
        "purpose": "Finalize the validation status after the human review decision.",
        "semantic": False,
        "prompt": "No LLM prompt is used. The system combines machine pre-checks and human review decisions into a final validation_status.",
        "input": "Machine validation report and human review decisions.",
        "output": {
            "final_valid_records": 5,
            "validation_status": "human_verified",
            "ready_for_storage": True,
        },
        "saved": "final_validation_status table",
        "note": "This step is displayed as completed only after human approval. It represents the business handover from AI-generated candidates to verified data.",
    },
    {
        "key": "save_relational_db",
        "phase": "structured_storage",
        "name": "save-relational-db",
        "short": "Publish structured event table",
        "purpose": "Store verified event data in relational form for dashboards, SQL queries and future Text-to-SQL interfaces.",
        "semantic": False,
        "prompt": "No LLM prompt is used. This is the relational storage step for verified structured data.",
        "input": "Human-validated event records with final validation_status.",
        "output": {
            "table": "llm_extracted_company_events",
            "records_saved": 5,
            "human_validated": True,
            "analysis_ready": True,
        },
        "saved": "Relational DB table: llm_extracted_company_events",
        "note": "Clicking this job shows the final structured event table below the pipeline. This table is the handover artifact to the separate Data Analysis View.",
    },
]


# Sample-document specific configuration used by the Engineering View.
# The PoC demonstrates the flow with one concrete official peer document rather
# than mixing several companies in the Human Review panel.
SAMPLE_DOCUMENT_CONTEXT = {
    "source_id": "SRC_ABF_AR_2025",
    "document_id": "doc_abf_annual_report_2025",
    "company_name": "ABF Sugar / Associated British Foods plc",
    "document_title": "Associated British Foods Annual Report 2025",
    "reporting_period": "52 weeks ended 13 September 2025",
    "sample_pdf_path": "/assets/comp/04_ABF/abf-annual-report-2025.pdf.downloadasset.pdf",
    "why_this_pdf": "It contains finance, risk, operations, investment and sustainability signals that directly explain the ABF Sugar 2025 peer benchmark used in the dashboard.",
}

PROMPT_CHAINS = {
    "metadata_extraction": [
        {
            "title": "Identify the source document",
            "prompt": "Read the title page, contents page and first operating-business overview. Extract the legal issuer, report title, publication year, reporting period, language and whether the document is an annual report. Return valid JSON only.",
            "input": "Filename, PDF metadata, pages 1-5 of ABF Annual Report 2025.",
            "output": {"issuer": "Associated British Foods plc", "document_title": "Annual Report 2025", "publication_year": 2025, "reporting_period": "52 weeks ended 13 September 2025", "language": "en", "document_type": "annual_report"},
            "saved": "document_metadata.source_identification",
        },
        {
            "title": "Map the relevant business scope",
            "prompt": "The dashboard is for Nordzucker competitive intelligence. From the annual report, identify which segment is relevant to sugar-industry peer analysis. Do not use Primark, Grocery, Ingredients or Agriculture unless needed as group context.",
            "input": "Operating business overview and contents page.",
            "output": {"relevant_segment": "Sugar", "segment_display_name": "ABF Sugar", "comparison_role": "peer competitor", "exclude_segments": ["Retail", "Grocery", "Ingredients", "Agriculture"]},
            "saved": "document_metadata.business_scope",
        },
        {
            "title": "Create extraction configuration",
            "prompt": "Create an extraction configuration for dashboard-linked events. Prioritise finance shock, restructuring, closure, capacity expansion, product diversification, regulatory exposure and decarbonisation. Keep page references.",
            "input": "Document metadata and dashboard analysis axes.",
            "output": {"target_axes": ["finance", "risk", "operations", "investment", "sustainability", "products/regulation"], "max_demo_events": 5, "page_reference_required": True},
            "saved": "ie_extraction_config.json",
        },
    ],
    "select_passages": [
        {
            "title": "Find sugar-segment sections",
            "prompt": "Select only passages that belong to ABF Sugar or explicitly explain ABF Sugar performance. Keep section title and page number. Ignore unrelated group segments unless the passage explains sugar-specific risk or investment.",
            "input": "Cleaned text blocks from the parsed annual report.",
            "output": {"selected_sections": ["Operating review – Sugar", "ESG at Sugar", "Board activities: acquisitions/disposals/projects"], "primary_pages": [34, 35, 36, 37, 38, 97]},
            "saved": "ie_candidate_sections.jsonl",
        },
        {
            "title": "Detect candidate event passages",
            "prompt": "Within the selected sections, mark passages containing concrete business events: numeric financial deterioration, restructuring, plant closure, capacity expansion, named investment projects, emissions-reduction projects or regulatory causes.",
            "input": "ABF Sugar sections around pages 34-38 and governance page 97.",
            "output": {"candidate_passages": 12, "examples": ["Sugar revenue and operating loss", "Azucarera footprint reduction", "Vivergo closure", "Ubombo debottlenecking", "British Sugar decarbonisation projects"]},
            "saved": "ie_candidate_passages.jsonl",
        },
        {
            "title": "Rank passages for the prototype",
            "prompt": "Rank candidate passages by strategic usefulness for Nordzucker. Keep a small representative set of roughly five records. Prefer passages that link to dashboard tabs and avoid creating a complete event database in this prototype.",
            "input": "Candidate passages with page numbers and event keywords.",
            "output": {"selected_for_demo": 5, "selection_reason": "Covers finance/risk shock, restructuring, regulation-linked closure, capacity expansion and decarbonisation."},
            "saved": "selected_demo_passages.json",
        },
    ],
    "extract_events_json": [
        {
            "title": "Extract draft event candidates",
            "prompt": "For each selected passage, extract a draft event with company_name, event_type, country, site_name, product_category, target_year, status, quantitative values and evidence_text. Use only facts explicitly supported by the passage.",
            "input": "Five selected ABF Sugar passages with page references.",
            "output": {"draft_events": ["financial_performance_warning", "plant_network_restructuring", "bioethanol_plant_closure", "capacity_expansion_and_efficiency_investment", "decarbonisation_project"]},
            "saved": "events_draft_raw.json",
        },
        {
            "title": "Normalize schema and controlled vocabulary",
            "prompt": "Normalize event_type, product_category, production_type, country and status to the project schema. Preserve original wording in evidence_text and do not overwrite uncertain city/site fields with hallucinated values.",
            "input": "Draft event candidates and schema vocabulary.",
            "output": {"normalized_records": 5, "fields_normalized": ["event_type", "country", "site_name", "product_category", "status"]},
            "saved": "events_normalized.json",
        },
        {
            "title": "Score confidence and flag review needs",
            "prompt": "Assign extraction_confidence between 0 and 1. Lower confidence if a field is inferred rather than explicitly stated. Add review_comment explaining what the human analyst should check.",
            "input": "Normalized event records and evidence snippets.",
            "output": {"records_scored": 5, "confidence_range": "0.91–0.95", "requires_human_review": True},
            "saved": "events_pending_human_review.json",
        },
    ],
    "link_evidence": [
        {
            "title": "Attach page-level evidence",
            "prompt": "For each event, attach the supporting annual-report page and the shortest evidence text that directly supports the record. Prefer exact source wording for numeric values and causal claims.",
            "input": "Normalized event records and selected source passages.",
            "output": {"linked_events": 5, "source_pages": [35, 36, 37], "missing_page_references": 0},
            "saved": "event_evidence_links.json",
        },
        {
            "title": "Check evidence sufficiency",
            "prompt": "Classify the evidence for each event as direct, indirect or insufficient. Direct means the source text supports the event type and the main quantitative or causal claim.",
            "input": "Event records with evidence_text and page links.",
            "output": {"direct_evidence": 5, "indirect_evidence": 0, "insufficient_evidence": 0},
            "saved": "evidence_quality_report.json",
        },
        {
            "title": "Prepare Human Review payload",
            "prompt": "Create the final review payload. Include only the five representative prototype events, the evidence text, source link, confidence and review comment. State that this is not an exhaustive extraction of all possible ABF events.",
            "input": "Evidence-linked events and quality report.",
            "output": {"human_review_records": 5, "extraction_scope": "representative prototype subset", "dashboard_linked": True},
            "saved": "engineering_sample_events.csv",
        },
    ],
}

SAMPLE_JOB_UPDATES = {
    "upload_pdf": {
        "short": "Upload ABF Annual Report 2025",
        "purpose": "Accept the selected sample PDF as the raw source document for the RAG and IE branches.",
        "input": "ABF Annual Report 2025 PDF selected through Upload PDF or downloaded via the Sample PDF button.",
        "output": {"document_id": "doc_abf_annual_report_2025", "file_name": DEFAULT_FILE, "source_type": "annual_report", "status": "uploaded"},
        "saved": "document_registry / document_id=doc_abf_annual_report_2025",
        "note": "The prototype uses this single official ABF PDF to avoid mixing events from several companies in the Human Review panel.",
    },
    "register_source": {
        "output": {"source_id": "SRC_ABF_AR_2025", "document_id": "doc_abf_annual_report_2025", "source_owner": "ABF Sugar / Associated British Foods plc", "comparison_role": "peer competitor for Nordzucker", "human_selected": True},
        "saved": "document_sources table / SRC_ABF_AR_2025",
    },
    "metadata_extraction": {
        "prompt": "Prompt chain shown below. The chain first identifies the annual report, then narrows the relevant comparison scope to ABF Sugar, and finally creates the extraction configuration for dashboard-linked events.",
        "output": {"company_name": "Associated British Foods plc", "relevant_peer_segment": "ABF Sugar", "document_title": "Annual Report 2025", "publication_year": 2025, "reporting_period": "52 weeks ended 13 September 2025", "document_type": "annual_report"},
    },
    "parse_pdf": {"output": {"pages_processed": 235, "layout_blocks": "simulated", "page_reference_mode": "annual-report page + PDF page + block_id"}},
    "extract_clean_text": {"output": {"text_blocks": "simulated", "cleaned": True, "metadata_fields": ["document_id", "source_id", "page", "section", "segment", "year"]}},
    "chunk_document": {"output": {"chunks_created": 162, "average_chunk_tokens": 420, "metadata_attached": True}},
    "create_embeddings": {"output": {"vectors_created": 162, "embedding_model": "conceptual placeholder in frontend PoC", "dimension": "not executed"}},
    "store_vector_db": {"output": {"collection": "official_company_documents", "upserted_vectors": 162, "retrieval_ready": True}},
    "prepare_retrieval": {"output": {"rag_query_ready": True, "future_frontend": "Interactive Dashboard / Chatbot", "implemented_now": "static prototype answers only"}},
    "select_passages": {
        "prompt": "Prompt chain shown below. It identifies ABF Sugar sections, detects candidate event passages and ranks a small subset for the prototype.",
        "output": {"candidate_passages": 12, "selected_demo_passages": 5, "pages_covered": [35, 36, 37], "event_keywords_detected": ["low European sugar prices", "restructuring", "closure", "debottlenecking", "decarbonisation"]},
        "saved": "selected_demo_passages.json",
    },
    "extract_events_json": {
        "prompt": "Prompt chain shown below. It extracts draft events, normalizes them to the project schema and assigns confidence plus review comments.",
        "output": [
            {"event_id": "ABF2025_EVT_001", "event_type": "financial_performance_warning", "source_page": "p. 35", "confidence": 0.94},
            {"event_id": "ABF2025_EVT_002", "event_type": "plant_network_restructuring", "source_page": "p. 35", "confidence": 0.91},
            {"event_id": "ABF2025_EVT_003", "event_type": "bioethanol_plant_closure", "source_page": "p. 35", "confidence": 0.95},
            {"event_id": "ABF2025_EVT_004", "event_type": "capacity_expansion_and_efficiency_investment", "source_page": "p. 36", "confidence": 0.93},
            {"event_id": "ABF2025_EVT_005", "event_type": "decarbonisation_project", "source_page": "p. 37", "confidence": 0.92},
        ],
        "saved": "events_pending_human_review.json",
    },
    "link_evidence": {
        "prompt": "Prompt chain shown below. It attaches source page links, checks evidence sufficiency and prepares the Human Review payload.",
        "output": {"events_with_evidence": 5, "missing_evidence": 0, "evidence_fields": ["source_page", "source_link", "source_text"]},
        "saved": "engineering_sample_events.csv",
    },
    "schema_precheck": {"output": {"records_checked": 5, "machine_check_passed": 5, "requires_human_review": 5}},
}

for _job in JOBS:
    if _job["key"] in PROMPT_CHAINS:
        _job["prompt_chain"] = PROMPT_CHAINS[_job["key"]]
    if _job["key"] in SAMPLE_JOB_UPDATES:
        _job.update(SAMPLE_JOB_UPDATES[_job["key"]])


PIPELINE_ORDER = [job["key"] for job in JOBS]
HUMAN_GATE_KEY = "human_review"
HUMAN_GATE_INDEX = PIPELINE_ORDER.index(HUMAN_GATE_KEY)

TUTORIAL_STEPS = [
    {
        "title": "1. Start the tutorial",
        "text": """
#### Welcome to the Data Engineering tutorial

This guided walkthrough explains how the prototype turns one official sample PDF into structured, human-verified event data for the analysis dashboard.

#### What you will see

- How to download and upload the supported sample PDF.
- How the simulated pipeline moves through document intake, RAG preparation, information extraction, human validation and structured storage.
- How LLM-related steps expose their prompt-chain checkpoints, inputs and outputs.

#### How to continue

Click **Next** to start the tutorial. Click **Skip tutorial** if you already know the workflow.
""",
        "hint": "You can reopen this walkthrough later by clicking the Tutorial button next to Sample PDF.",
    },
    {
        "title": "2. Download the sample PDF",
        "media": "GIF: Sample PDF download",
        "media_src": "/assets/tutorial/01_download_sample_pdf.gif",
        "media_alt": "Tutorial GIF showing the Sample PDF button being clicked to download the ABF Annual Report 2025 sample document.",
        "text": """
#### Goal

Download the official sample document used by this prototype: **ABF Annual Report 2025**.

#### What to do

Click **Sample PDF**. The browser downloads the supported PDF file, which is then used in the next upload step.

#### Why this matters

The prototype is intentionally configured around one concrete source document. This keeps the pipeline outputs, prompt-chain examples, Human Review records and dashboard evidence aligned with the same PDF instead of mixing several companies or sources.
""",
        "hint": "If the browser adds a suffix such as “(1)” to the filename, the upload step still accepts it as long as the filename starts with “abf-annual-report-2025”.",
    },
    {
        "title": "3. Upload the sample PDF",
        "media": "GIF: Sample PDF upload",
        "media_src": "/assets/tutorial/02_upload_sample_pdf.gif",
        "media_alt": "Tutorial GIF showing the downloaded ABF Annual Report 2025 sample PDF being uploaded through the Upload PDF box.",
        "text": """
#### Goal

Start the simulated document-processing pipeline with the supported sample PDF.

#### What to do

Upload the downloaded ABF Annual Report 2025 file through the **Upload PDF** box. Once the valid file is selected, the pipeline starts automatically.

#### What this represents

In a production system, this step would register the PDF, store the source document and create a stable document ID. In this prototype, no real PDF parsing or backend storage is executed; the app shows the intended processing flow with preconfigured outputs.
""",
        "hint": "Only the sample PDF is supported. Other PDFs show a warning modal and do not start the pipeline because the prompt-chain outputs and review records are prepared for this document.",
    },
    {
        "title": "4. Watch the pipeline progress",
        "media": "GIF: pipeline progress",
        "media_src": "/assets/tutorial/03_pipeline_overview.gif",
        "media_alt": "Tutorial GIF showing the simulated Data Engineering pipeline progressing from source intake through RAG indexing, information extraction, human validation and structured storage.",
        "text": """
#### Goal

Understand the overall processing sequence from PDF intake to analysis-ready structured data.

#### How to read the pipeline

Green check marks indicate completed jobs, spinning indicators show running jobs, and the Human Review step acts as the manual validation gate. The upper branch illustrates RAG-oriented indexing, while the lower branch illustrates information extraction, validation and storage.

#### Business meaning

The key idea is separation of responsibilities: document preparation and retrieval indexing create searchable evidence, while the IE branch creates structured event candidates that must still be reviewed by a human analyst before they are used in dashboards.
""",
        "hint": "This GIF focuses on the pipeline advancing. The next step shows how to inspect the prompt and output behind individual pipeline jobs.",
    },
    {
        "title": "5. Inspect Prompt and Output for a pipeline job",
        "media": "GIF: prompt and output detail",
        "media_src": "/assets/tutorial/04_pipeline_prompt_output.gif",
        "media_alt": "Tutorial GIF showing a pipeline job being clicked and the corresponding Prompt and Output areas highlighted with red boxes.",
        "text": """
#### Goal

See how LLM-related pipeline steps are made transparent instead of being shown as a black box.

#### What to do

Click a pipeline job such as **extract-metadata**, **select-passages**, **extract-events-json** or **link-evidence**. The detail panel below the pipeline shows the configured prompt-chain steps, inputs, saved artifacts and mock outputs.

#### What to look for

The GIF highlights the **Prompt** and **Output** areas with red boxes. These areas show which instruction would be sent to the LLM and what intermediate result would be produced before the next validation or extraction step.
""",
        "hint": "Some semantic jobs contain multiple prompt-chain buttons. Expanding them shows how the task is split into smaller, auditable LLM checkpoints.",
    },
    {
        "title": "6. Review the human validation gate",
        "media": "GIF placeholder: human-review gate",
        "text": """
#### Goal

Understand why the pipeline deliberately stops before storing extracted events as final data.

#### What happens here

The Human Review panel shows extracted event candidates together with the supporting evidence text. The analyst checks whether the fields, numbers, event type and source reference are actually supported by the PDF.

#### Why this matters

LLM extraction can produce plausible but incomplete or wrongly structured records. The validation gate prevents draft extraction output from being treated as reliable competitive-intelligence data without human confirmation.
""",
        "hint": "Machine schema checks are useful, but they do not replace a business review of the evidence and extracted meaning.",
    },
    {
        "title": "7. Confirm representative extracted records",
        "media": "GIF placeholder: confirmation workflow",
        "text": """
#### Goal

Confirm a small representative sample of extracted ABF Sugar events.

#### What is shown

The prototype displays five review records linked to dashboard-relevant topics: margin deterioration, restructuring, plant closure, capacity expansion and decarbonisation. These records demonstrate the validation workflow without trying to extract every possible KPI or event from the full annual report.

#### How to use it

Review each record against its evidence text, edit fields if necessary, and confirm the record. A full production system would repeat this process for a larger set of extracted candidates and persist the review history.
""",
        "hint": "The five records are illustrative prototype examples, not a complete extraction of all possible events in the ABF Annual Report 2025.",
    },
    {
        "title": "8. Check the final structured output",
        "media": "GIF placeholder: final table",
        "text": """
#### Goal

See the handover from human-validated extraction results to analysis-ready structured data.

#### What happens after validation

Once the review gate is completed, the pipeline continues to **validation-complete** and **save-relational-db**. The final table represents the structured event records that would be stored for dashboards, SQL queries or future retrieval-supported analysis.

#### Business meaning

The final output is no longer just document text. It is a structured, source-linked dataset that can support competitive analysis, evidence tables, dashboard filters and future interactive question answering.
""",
        "hint": "The current app uses preconfigured prototype data, but the workflow shows the intended handover from official documents to analysis-ready data.",
    },
]


def initial_state():
    return {"filename": None, "progress": 0, "started": False, "run_id": None}


def is_supported_sample_pdf(filename):
    """Return True when the uploaded file is the supported sample PDF.

    Browser downloads may append suffixes such as ``(1)`` before the
    extension. The prototype therefore checks the beginning of the filename
    rather than requiring an exact match.
    """
    if not filename:
        return False
    name = Path(str(filename)).name.lower().strip()
    normalized = name.replace("_", " ").replace("-", "-")
    return any(name.startswith(prefix) or normalized.startswith(prefix) for prefix in SUPPORTED_SAMPLE_PREFIXES)


def unsupported_pdf_message(filename):
    return [
        html.Strong("Unsupported PDF for this prototype. "),
        html.Span(
            "This Data Engineering workflow is configured only for the sample PDF "
            "'ABF Annual Report 2025'. Please use the Sample PDF button next to Tutorial, "
            "then upload that file. If your browser added a suffix such as '(1)', it will still be accepted."
        ),
        html.Div(f"Selected file: {filename}", className="mt-2 small text-muted") if filename else "",
    ]


def human_gate_approved(approval_data):
    return bool((approval_data or {}).get("approved", False))


def job_index(key):
    for idx, job in enumerate(JOBS):
        if job["key"] == key:
            return idx
    return 0


def job_status(index, state, approval_data=None):
    progress = int((state or {}).get("progress", 0))
    started = bool((state or {}).get("started", False))
    approved = human_gate_approved(approval_data)

    # When the user comes back to the page after approval, the page-local
    # progress store may be reset. The global session approval store should
    # still show the whole pipeline as completed.
    if approved and progress == 0 and not started:
        return "completed"

    if not approved and progress >= HUMAN_GATE_INDEX:
        if index < HUMAN_GATE_INDEX:
            return "completed"
        if index == HUMAN_GATE_INDEX:
            return "warning"
        return "pending"

    if index < progress:
        return "completed"
    if started and index == progress:
        return "running"
    return "pending"

def status_icon(status):
    if status == "completed":
        return "✓"
    if status == "warning":
        return "!"
    if status == "running":
        return ""
    return ""


def json_pretty(value):
    return json.dumps(value, indent=2, ensure_ascii=False)


def jobs_for_phase(phase):
    return [j for j in JOBS if j["phase"] == phase]


def find_event(records, event_id):
    for rec in records:
        if rec.get("event_id") == event_id:
            return rec
    return records[0] if records else {}


def event_records():
    records = events.where(pd.notnull(events), "").to_dict("records")
    for rec in records:
        rec["human_verified"] = str(rec.get("human_verified", "False"))
    return records


def normalize_review_records(records=None):
    """Return browser-store friendly review records.

    The app is intended for Render deployment without a database. Therefore
    human edits are kept in dcc.Store(session) and copied into the global
    approval payload once the review gate is confirmed.
    """
    normalized = copy.deepcopy(records) if records else event_records()
    for rec in normalized:
        rec["human_verified"] = str(rec.get("human_verified", "False"))
        if rec["human_verified"].lower() == "true":
            rec["human_verified"] = "True"
        elif rec["human_verified"].lower() == "false":
            rec["human_verified"] = "False"
        rec.setdefault("validation_status", "pending_review")
        rec.setdefault("review_comment", "")
    return normalized


def update_review_record(records, event_id, values, mark_confirmed=False):
    updated = []
    for rec in normalize_review_records(records):
        if rec.get("event_id") == event_id:
            rec = {**rec, **{k: (v if v is not None else "") for k, v in values.items()}}
            rec["edited_in_session"] = True
            rec["last_review_action_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
            if mark_confirmed:
                rec["human_verified"] = "True"
                rec["validation_status"] = "human_verified"
        updated.append(rec)
    return updated


def mark_records_reviewed(records, required_ids=None):
    required = set(required_ids or [])
    reviewed = []
    for rec in normalize_review_records(records):
        if not required or rec.get("event_id") in required:
            rec = {
                **rec,
                "human_verified": "True",
                "validation_status": "human_verified",
                "edited_in_session": rec.get("edited_in_session", False),
                "last_review_action_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
        reviewed.append(rec)
    return reviewed


def phase_context(phase, state, approval_data=None):
    phase_jobs = jobs_for_phase(phase)
    if not phase_jobs:
        return None
    progress = int((state or {}).get("progress", 0))
    approved = human_gate_approved(approval_data)
    started = bool((state or {}).get("started", False))
    if approved and progress == 0 and not started:
        visible_jobs = phase_jobs
    else:
        visible_jobs = [j for j in phase_jobs if job_index(j["key"]) < progress or job_status(job_index(j["key"]), state, approval_data) in {"running", "warning", "completed"}]
    if not visible_jobs:
        return html.Div("waiting for upstream phase", className="phase-context muted")
    current = visible_jobs[-1]
    return html.Div(
        [
            html.Div(current["short"], className="phase-context-title"),
            html.Div(f"Artifact: {current['saved']}", className="phase-context-artifact"),
        ],
        className="phase-context",
    )


def render_metric_cards(state, approval_data=None):
    progress = int((state or {}).get("progress", 0))
    started = bool((state or {}).get("started", False))
    approved = human_gate_approved(approval_data)

    if approved and progress == 0 and not started:
        completed = len(JOBS)
        status = "completed"
    else:
        completed = min(progress, len(JOBS))
        if not approved and completed >= HUMAN_GATE_INDEX:
            status = "waiting for human validation"
        elif started:
            status = "running"
        elif completed == len(JOBS):
            status = "completed"
        else:
            status = "waiting"

    return dbc.Row(
        [
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("Status", className="kpi-title"), html.Div(status, className="kpi-value-small"), html.Div("frontend simulation", className="kpi-sub")])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("Jobs", className="kpi-title"), html.Div(f"{completed}/{len(JOBS)}", className="kpi-value-small"), html.Div("pipeline progress", className="kpi-sub")])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("RAG", className="kpi-title"), html.Div("conceptual", className="kpi-value-small"), html.Div("VectorDB not implemented", className="kpi-sub")])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("IE", className="kpi-title"), html.Div("human gate", className="kpi-value-small"), html.Div("manual approval required", className="kpi-sub")])), md=3),
        ],
        className="metric-row compact-metric-row",
    )

def render_phase_card(phase, state, approval_data=None, linear=False):
    rows = []
    for job in jobs_for_phase(phase):
        idx = job_index(job["key"])
        status = job_status(idx, state, approval_data)
        rows.append(
            html.Button(
                [
                    html.Span([html.Span(status_icon(status), className=f"job-status {status}"), html.Span(job["name"], className="job-name")], className="job-left"),
                    html.Span("↻", className="job-retry"),
                ],
                id={"type": "pipeline-job", "key": job["key"]},
                className=f"job-row {status}",
                n_clicks=0,
                title=job["short"],
            )
        )
    card_class = "gitlab-stage-card linear-stage-card" if linear else "gitlab-stage-card"
    return html.Div(
        [
            html.Div([html.Div(PHASE_LABELS[phase], className="stage-title"), html.Div(f"{len(jobs_for_phase(phase))} jobs", className="stage-count")], className="stage-header"),
            html.Div(rows, className="stage-jobs"),
            phase_context(phase, state, approval_data),
        ],
        className=card_class,
    )


def render_pipeline(state, approval_data=None):
    return html.Div(
        [
            html.Div(
                [
                    render_phase_card("source_intake", state, approval_data, linear=True),
                    render_phase_card("text_preparation", state, approval_data, linear=False),
                ],
                className="pipeline-left-root common-phase-row",
            ),
            html.Div(
                [
                    html.Div(className="branching-line-root"),
                    html.Div(className="branching-dot"),
                    html.Div(className="branching-line-vertical"),
                    html.Div(className="branching-line-top"),
                    html.Div(className="branching-line-bottom"),
                ],
                className="branching-connector",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("RAG branch: retrieval-oriented document index", className="branch-lane-label"),
                            html.Div([render_phase_card(phase, state, approval_data, linear=True) for phase in RAG_PHASES], className="branch-stage-row"),
                        ],
                        className="branch-lane rag-lane",
                    ),
                    html.Div(
                        [
                            html.Div("IE branch: extraction → human validation → storage", className="branch-lane-label"),
                            html.Div([render_phase_card(phase, state, approval_data, linear=True) for phase in IE_PHASES], className="branch-stage-row ie-stage-row"),
                        ],
                        className="branch-lane ie-lane",
                    ),
                ],
                className="branching-right-zone",
            ),
        ],
        className="branching-pipeline",
    )


def render_prompt_chain(job):
    chain = job.get("prompt_chain") or []
    items = []
    for idx, step in enumerate(chain, start=1):
        items.append(
            dbc.AccordionItem(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div("Prompt", className="section-label"),
                                    html.Pre(step.get("prompt", ""), className="prompt-box prompt-chain-prompt"),
                                ],
                                md=5,
                            ),
                            dbc.Col(
                                [
                                    html.Div("Input", className="section-label"),
                                    html.Div(step.get("input", ""), className="soft-box"),
                                    html.Div("Saved artifact", className="section-label mt-3"),
                                    html.Div(step.get("saved", ""), className="soft-box"),
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    html.Div("Mock output / checkpoint", className="section-label"),
                                    html.Pre(json_pretty(step.get("output", {})), className="json-box"),
                                ],
                                md=4,
                            ),
                        ]
                    )
                ],
                title=f"{idx}. {step.get('title', 'Prompt step')}",
                item_id=f"{job['key']}-prompt-{idx}",
            )
        )
    return dbc.Accordion(items, start_collapsed=True, always_open=True, className="prompt-chain-accordion")


def semantic_detail(job):
    if job["semantic"]:
        if job.get("prompt_chain"):
            return html.Div(
                [
                    dbc.Alert(
                        [
                            html.Strong("LLM prompt chain simulation. "),
                            "This semantic job is shown as multiple smaller prompts so that intermediate checkpoints remain inspectable before the final event table is created.",
                        ],
                        color="info",
                        className="py-2",
                    ),
                    render_prompt_chain(job),
                    dbc.Row(
                        [
                            dbc.Col([html.Div("Job-level input", className="section-label"), html.Div(job["input"], className="soft-box")], md=4),
                            dbc.Col([html.Div("Saved artifact", className="section-label"), html.Div(job["saved"], className="soft-box")], md=3),
                            dbc.Col([html.Div("Aggregated mock output", className="section-label"), html.Pre(json_pretty(job["output"]), className="json-box")], md=5),
                        ],
                        className="mt-3",
                    ),
                ]
            )
        left_title = "Prompt used"
        left_body = job["prompt"]
    else:
        left_title = "Implementation note"
        left_body = f"{job['prompt']}\n\nTo be decided / relevant implementation issue:\n{job['note']}"

    return dbc.Row(
        [
            dbc.Col([html.Div(left_title, className="section-label"), html.Pre(left_body, className="prompt-box")], md=5),
            dbc.Col([html.Div("Input", className="section-label"), html.Div(job["input"], className="soft-box"), html.Div("Saved artifact", className="section-label mt-3"), html.Div(job["saved"], className="soft-box")], md=3),
            dbc.Col([html.Div("Mock output / result", className="section-label"), html.Pre(json_pretty(job["output"]), className="json-box")], md=4),
        ]
    )


def human_review_panel(approval_data=None):
    records = normalize_review_records()
    first = records[0]["event_id"] if records else None
    approved = human_gate_approved(approval_data)
    required_ids = [r.get("event_id") for r in records if r.get("event_id")]
    status_alert = dbc.Alert(
        "Human validation has already been approved. The pipeline can continue.",
        color="success",
        className="py-2",
    ) if approved else dbc.Alert(
        "Human validation required. Confirm each extracted event from the dropdown, then click Confirm all reviewed events.",
        color="warning",
        className="py-2",
    )
    prototype_scope_alert = dbc.Alert(
        [
            html.Strong("Prototype extraction scope. "),
            "The Human Review panel uses ABF Annual Report 2025 as the sample PDF and shows five representative, dashboard-linked events only. It does not claim to extract every possible event or KPI from the report.",
        ],
        color="info",
        className="py-2",
    )
    return html.Div(
        [
            status_alert,
            prototype_scope_alert,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Extracted event"),
                            dcc.Dropdown(
                                id="ep-review-event-id",
                                options=[{"label": f"{r.get('event_id')} | {r.get('company_name')} | {r.get('event_type')}", "value": r.get("event_id")} for r in records],
                                value=first,
                                clearable=False,
                            ),
                            html.Div(id="ep-review-evidence", className="source-preview-box mt-3"),
                            dbc.Button("Save & confirm selected event", id="ep-confirm-selected-event", color="primary", outline=True, size="sm", className="mt-2", n_clicks=0),
                            html.Div(id="ep-confirm-status", className="status-text mt-2"),
                        ],
                        md=5,
                    ),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dbc.Col([dbc.Label("company_name"), dbc.Input(id="ep-review-company", type="text")], md=6),
                                    dbc.Col([dbc.Label("event_type"), dbc.Input(id="ep-review-event-type", type="text")], md=6),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col([dbc.Label("country"), dbc.Input(id="ep-review-country", type="text")], md=4),
                                    dbc.Col([dbc.Label("city"), dbc.Input(id="ep-review-city", type="text")], md=4),
                                    dbc.Col([dbc.Label("site_name"), dbc.Input(id="ep-review-site", type="text")], md=4),
                                ],
                                className="mt-2",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col([dbc.Label("product_category"), dbc.Input(id="ep-review-product", type="text")], md=4),
                                    dbc.Col([dbc.Label("target_year"), dbc.Input(id="ep-review-year", type="text")], md=4),
                                    dbc.Col([dbc.Label("status"), dbc.Input(id="ep-review-status-field", type="text")], md=4),
                                ],
                                className="mt-2",
                            ),
                            dbc.Label("review_comment", className="mt-2"),
                            dbc.Textarea(id="ep-review-comment", rows=2),
                            dbc.Button("Save edits only", id="ep-save-selected-event", color="secondary", outline=True, size="sm", className="mt-2" , n_clicks=0),
                            html.Div(id="ep-confirmation-progress", className="mt-3"),
                            dbc.Button("Confirm all reviewed events", id="ep-confirm-all-reviewed", color="success", className="mt-2", n_clicks=0),
                            html.Div(id="ep-inline-approve-status", className="status-text mt-2"),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("Confirm all events?")),
                                    dbc.ModalBody(
                                        [
                                            html.P("Some extracted events have not been individually confirmed yet."),
                                            html.Div(id="ep-missing-events-modal-text", className="missing-events-box"),
                                            html.P("You can still approve the full Human Review gate. This means all event records are treated as reviewed for this session."),
                                        ]
                                    ),
                                    dbc.ModalFooter(
                                        [
                                            dbc.Button("Go back and review individually", id="ep-cancel-confirm-all-modal", color="secondary", outline=True, className="me-2", n_clicks=0),
                                            dbc.Button("Confirm all anyway", id="ep-force-confirm-all", color="success", n_clicks=0),
                                        ]
                                    ),
                                ],
                                id="ep-confirm-all-modal",
                                centered=True,
                                is_open=False,
                            ),
                        ],
                        md=7,
                    ),
                ]
            ),
        ]
    )

def final_table_panel(approval_data=None):
    approved = human_gate_approved(approval_data)
    reviewed_records = (approval_data or {}).get("reviewed_records")
    if approved and reviewed_records:
        df = pd.DataFrame(normalize_review_records(reviewed_records))
    else:
        df = events.copy()
        if approved:
            df["human_verified"] = True
            df["validation_status"] = "human_verified"
    alert = dbc.Alert(
        [
            html.Strong("Final structured event table after human validation. "),
            "For Render deployment no server-side database is required: the approved records are kept in the browser session store and can be exported as CSV.",
        ],
        color="success" if approved else "warning",
    )
    if not approved:
        alert = dbc.Alert("Structured storage is blocked until Human Review & Validation is approved. The table below is a preview only.", color="warning")
    return html.Div(
        [
            alert,
            data_note("browser session store → downloadable validated CSV / structured event output", llm_note=True),
            html.Div(
                [
                    dbc.Button("Download validated CSV", id="ep-download-review-csv", color="success", outline=True, size="sm", n_clicks=0, disabled=not approved),
                    dcc.Download(id="ep-download-reviewed-events"),
                ],
                className="mb-2",
            ),
            compact_table(df, FINAL_TABLE_COLUMNS, llm_columns=LLM_EVENT_COLUMNS, page_size=8),
        ]
    )


def detail_panel(job_key, state, approval_data=None):
    selected = next((j for j in JOBS if j["key"] == job_key), JOBS[0])
    idx = job_index(selected["key"])
    status = job_status(idx, state or {}, approval_data)
    if selected["key"] == "human_review":
        body = human_review_panel(approval_data)
    elif selected["key"] == "save_relational_db":
        body = final_table_panel(approval_data)
    else:
        body = semantic_detail(selected)

    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.Div([html.Span(PHASE_LABELS[selected["phase"]], className="detail-stage-pill"), html.Span(selected["name"], className="detail-title")]),
                        html.Span(status, className=f"detail-status {status}"),
                    ],
                    className="detail-header-row",
                )
            ),
            dbc.CardBody(
                [
                    html.P(selected["purpose"], className="detail-purpose"),
                    body,
                ]
            ),
        ],
        className="detail-card",
    )



def tutorial_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(id="ep-tutorial-title")),
            dbc.ModalBody(
                [
                    html.Div(id="ep-tutorial-progress", className="tutorial-progress-text"),
                    html.Div(id="ep-tutorial-media", className="tutorial-media-placeholder"),
                    html.Div(id="ep-tutorial-text", className="tutorial-main-text"),
                    html.Div(id="ep-tutorial-hint", className="tutorial-hint-box"),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Skip tutorial", id="ep-tutorial-skip", color="secondary", outline=True, className="me-auto", n_clicks=0),
                    dbc.Button("Previous", id="ep-tutorial-prev", color="secondary", outline=True, n_clicks=0),
                    dbc.Button("Next", id="ep-tutorial-next", color="primary", n_clicks=0),
                ]
            ),
        ],
        id="ep-tutorial-modal",
        centered=True,
        size="xl",
        backdrop="static",
        keyboard=False,
        is_open=True,
    )


def layout():
    return html.Div(
        [
            dcc.Store(id="ep-pipeline-state", data=initial_state()),
            dcc.Store(id="ep-review-records-store", storage_type="session", data=normalize_review_records()),
            dcc.Store(id="ep-confirmed-events", storage_type="session", data=[]),
            dcc.Store(id="ep-required-events", data=[r.get("event_id") for r in normalize_review_records() if r.get("event_id")]),
            dcc.Store(id="ep-tutorial-store", storage_type="session", data={"open": True, "step": 0, "completed": False}),
            dcc.Interval(id="ep-pipeline-timer", interval=850, n_intervals=0, disabled=True),
            tutorial_modal(),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Only the sample PDF is supported")),
                    dbc.ModalBody(html.Div(id="ep-unsupported-pdf-message")),
                    dbc.ModalFooter(
                        dbc.Button("OK", id="ep-unsupported-pdf-close", color="primary", n_clicks=0)
                    ),
                ],
                id="ep-unsupported-pdf-modal",
                is_open=False,
                centered=True,
            ),

            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Div("Data Engineering Pipeline", className="compact-page-title"),
                                            html.Div(
                                                "PDF upload → common preprocessing → RAG / IE branches → human validation gate",
                                                className="compact-page-subtitle",
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button("Tutorial", id="ep-open-tutorial", color="info", outline=True, size="sm", n_clicks=0, className="me-1"),
                                            dbc.Button("Sample PDF", id="ep-download-sample-pdf", color="success", outline=True, size="sm", n_clicks=0),
                                            dcc.Download(id="ep-download-sample-pdf-file"),
                                        ],
                                        md=2,
                                        className="compact-tutorial-col sample-pdf-col",
                                    ),
                                    dbc.Col(
                                        [
                                            dcc.Upload(
                                                id="ep-pdf-upload",
                                                children=html.Div(["Upload PDF"], className="compact-upload-label"),
                                                className="upload-box compact-upload-box",
                                                multiple=False,
                                                accept="application/pdf",
                                            ),
                                        ],
                                        md=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button("Reset", id="ep-reset-pipeline", color="secondary", outline=True, size="sm", n_clicks=0),
                                            html.Div(id="ep-upload-status", className="status-text compact-status-text"),
                                        ],
                                        md=2,
                                    ),
                                    dbc.Col(html.Div(id="ep-metric-cards"), md=3),
                                ],
                                className="align-items-center g-2",
                            ),
                            html.Hr(className="compact-divider"),
                            html.Div(id="ep-pipeline-view"),
                            html.Div(id="ep-human-gate-message"),
                        ]
                    )
                ],
                className="compact-engineering-top",
            ),

            html.Div(id="ep-job-detail"),
        ]
    )


@callback(
    Output("ep-download-sample-pdf-file", "data"),
    Input("ep-download-sample-pdf", "n_clicks"),
    prevent_initial_call=True,
)
def download_sample_pdf(n_clicks):
    if not n_clicks:
        return dash.no_update
    if not SAMPLE_PDF_PATH.exists():
        return dash.no_update
    return dcc.send_file(str(SAMPLE_PDF_PATH), filename=DEFAULT_FILE)


@callback(
    Output("ep-tutorial-store", "data"),
    Input("ep-open-tutorial", "n_clicks"),
    Input("ep-tutorial-skip", "n_clicks"),
    Input("ep-tutorial-prev", "n_clicks"),
    Input("ep-tutorial-next", "n_clicks"),
    State("ep-tutorial-store", "data"),
    prevent_initial_call=True,
)
def update_tutorial_state(open_clicks, skip_clicks, prev_clicks, next_clicks, store):
    store = store or {"open": True, "step": 0, "completed": False}
    step = int(store.get("step", 0))
    trigger = ctx.triggered_id

    if trigger == "ep-open-tutorial":
        return {"open": True, "step": 0, "completed": False}

    if trigger == "ep-tutorial-skip":
        return {**store, "open": False, "completed": True}

    if trigger == "ep-tutorial-prev":
        return {**store, "open": True, "step": max(step - 1, 0)}

    if trigger == "ep-tutorial-next":
        if step >= len(TUTORIAL_STEPS) - 1:
            return {**store, "open": False, "completed": True}
        return {**store, "open": True, "step": min(step + 1, len(TUTORIAL_STEPS) - 1)}

    return store


@callback(
    Output("ep-tutorial-modal", "is_open"),
    Output("ep-tutorial-title", "children"),
    Output("ep-tutorial-progress", "children"),
    Output("ep-tutorial-media", "children"),
    Output("ep-tutorial-text", "children"),
    Output("ep-tutorial-hint", "children"),
    Output("ep-tutorial-prev", "disabled"),
    Output("ep-tutorial-next", "children"),
    Input("ep-tutorial-store", "data"),
)
def render_tutorial(store):
    store = store or {"open": True, "step": 0, "completed": False}
    step = min(max(int(store.get("step", 0)), 0), len(TUTORIAL_STEPS) - 1)
    item = TUTORIAL_STEPS[step]
    is_last = step == len(TUTORIAL_STEPS) - 1

    return (
        bool(store.get("open", True)),
        item["title"],
        f"Step {step + 1} of {len(TUTORIAL_STEPS)}",
        html.Img(
            src=item["media_src"],
            alt=item.get("media_alt", item.get("media", "Tutorial media")),
            className="tutorial-media-image",
        ) if item.get("media_src") else (
            html.Div(
                [
                    html.Div(item.get("media", ""), className="tutorial-media-label"),
                    html.Div("GIF / screenshot can be added later here.", className="tutorial-media-subtitle"),
                ]
            ) if item.get("media") else None
        ),
        dcc.Markdown(item["text"], className="tutorial-markdown"),
        item["hint"],
        step == 0,
        "Finish" if is_last else "Next",
    )



@callback(
    Output("ep-pipeline-state", "data"),
    Output("ep-pipeline-timer", "disabled"),
    Output("global-human-validation-store", "data", allow_duplicate=True),
    Output("ep-unsupported-pdf-modal", "is_open"),
    Output("ep-unsupported-pdf-message", "children"),
    Input("ep-pdf-upload", "filename"),
    Input("ep-reset-pipeline", "n_clicks"),
    Input("ep-pipeline-timer", "n_intervals"),
    Input("ep-unsupported-pdf-close", "n_clicks"),
    State("ep-pipeline-state", "data"),
    State("global-human-validation-store", "data"),
    prevent_initial_call=True,
)
def update_pipeline_state(filename, reset_clicks, timer_ticks, modal_close_clicks, state, approval_data):
    trigger = ctx.triggered_id
    state = state or initial_state()
    approved = human_gate_approved(approval_data)

    if trigger == "ep-unsupported-pdf-close":
        return state, True, dash.no_update, False, dash.no_update

    if trigger == "ep-reset-pipeline":
        return initial_state(), True, {"approved": False}, False, ""

    if trigger == "ep-pdf-upload":
        if not filename:
            return state, True, dash.no_update, False, ""
        selected = filename
        if not is_supported_sample_pdf(selected):
            return state, True, dash.no_update, True, unsupported_pdf_message(selected)
        return {"filename": selected, "progress": 0, "started": True, "run_id": datetime.utcnow().strftime("%Y%m%d%H%M%S")}, False, {"approved": False}, False, ""

    if trigger == "ep-pipeline-timer":
        if not state.get("started"):
            return state, True, dash.no_update, False, dash.no_update
        next_progress = min(int(state.get("progress", 0)) + 1, len(JOBS))

        # Before human approval, the automated pipeline stops at the human-review gate.
        if next_progress >= HUMAN_GATE_INDEX and not approved:
            state = {**state, "progress": HUMAN_GATE_INDEX, "started": False}
            return state, True, dash.no_update, False, dash.no_update

        state = {**state, "progress": next_progress}
        if next_progress >= len(JOBS):
            state["started"] = False
            return state, True, dash.no_update, False, dash.no_update
        return state, False, dash.no_update, False, dash.no_update

    return state, True, dash.no_update, False, dash.no_update


@callback(
    Output("ep-review-records-store", "data", allow_duplicate=True),
    Output("ep-confirmed-events", "data", allow_duplicate=True),
    Input("ep-reset-pipeline", "n_clicks"),
    prevent_initial_call=True,
)
def reset_review_session(reset_clicks):
    if not reset_clicks:
        return dash.no_update, dash.no_update
    return normalize_review_records(), []


@callback(
    Output("ep-pipeline-view", "children"),
    Output("ep-upload-status", "children"),
    Output("ep-metric-cards", "children"),
    Output("ep-human-gate-message", "children"),
    Input("ep-pipeline-state", "data"),
    Input("global-human-validation-store", "data"),
)
def update_pipeline_view(state, approval_data):
    state = state or initial_state()
    filename = state.get("filename")
    progress = int(state.get("progress", 0))
    approved = human_gate_approved(approval_data)

    if approved:
        approved_event = (approval_data or {}).get("approved_event_id", "reviewed event")
        status = f"Human validation approved for {approved_event}. Pipeline displayed as completed for this session."
    elif filename:
        status = f"Selected document: {filename} | completed jobs: {progress}/{len(JOBS)}"
    else:
        status = "Upload a PDF to start the simulated pipeline. No real PDF parsing, embeddings, LLM API calls or DB writes are executed in this frontend PoC."

    if progress >= HUMAN_GATE_INDEX and not approved:
        gate_message = dbc.Alert(
            [
                html.Strong("Human validation required. "),
                "Click the yellow human-review job, confirm each extracted event, and then click Confirm all reviewed events."
            ],
            color="warning",
            className="mt-3",
        )
    elif approved:
        gate_message = dbc.Alert("Human validation approved. The remaining publication jobs continue with the same simulated pipeline timing.", color="success", className="mt-3")
    else:
        gate_message = ""

    return render_pipeline(state, approval_data), status, render_metric_cards(state, approval_data), gate_message


@callback(
    Output("ep-job-detail", "children"),
    Input({"type": "pipeline-job", "key": ALL}, "n_clicks"),
    Input("ep-pipeline-state", "data"),
    Input("global-human-validation-store", "data"),
)
def update_job_detail(_clicks, state, approval_data):
    state = state or initial_state()
    trigger = ctx.triggered_id
    if isinstance(trigger, dict) and trigger.get("type") == "pipeline-job":
        key = trigger.get("key")
    else:
        progress = int(state.get("progress", 0))
        if human_gate_approved(approval_data):
            key = "save_relational_db"
        elif progress >= HUMAN_GATE_INDEX:
            key = "human_review"
        else:
            key = JOBS[min(max(progress - 1, 0), len(JOBS) - 1)]["key"]
    return detail_panel(key, state, approval_data)


@callback(
    Output("ep-review-company", "value"),
    Output("ep-review-event-type", "value"),
    Output("ep-review-country", "value"),
    Output("ep-review-city", "value"),
    Output("ep-review-site", "value"),
    Output("ep-review-product", "value"),
    Output("ep-review-year", "value"),
    Output("ep-review-status-field", "value"),
    Output("ep-review-comment", "value"),
    Output("ep-review-evidence", "children"),
    Input("ep-review-event-id", "value"),
    State("ep-review-records-store", "data"),
    prevent_initial_call=False,
)
def populate_inline_review(event_id, review_records):
    records = normalize_review_records(review_records)
    rec = find_event(records, event_id)
    evidence = html.Div(
        [
            html.Div("Evidence text", className="section-label"),
            html.Blockquote(rec.get("source_text", ""), className="source-quote"),
            dcc.Markdown(rec.get("source_link", ""), className="source-link-text", link_target="_blank"),
            html.Div(f"Source page: {rec.get('source_page', '')} | Confidence: {rec.get('extraction_confidence', '')}", className="generated-by"),
        ]
    )
    return (
        rec.get("company_name", ""),
        rec.get("event_type", ""),
        rec.get("country", ""),
        rec.get("city", ""),
        rec.get("site_name", ""),
        rec.get("product_category", ""),
        str(rec.get("target_year", "")),
        rec.get("status", ""),
        rec.get("review_comment", ""),
        evidence,
    )


@callback(
    Output("ep-review-records-store", "data"),
    Output("ep-confirmed-events", "data"),
    Output("ep-confirm-status", "children"),
    Input("ep-save-selected-event", "n_clicks"),
    Input("ep-confirm-selected-event", "n_clicks"),
    State("ep-review-event-id", "value"),
    State("ep-review-records-store", "data"),
    State("ep-confirmed-events", "data"),
    State("ep-review-company", "value"),
    State("ep-review-event-type", "value"),
    State("ep-review-country", "value"),
    State("ep-review-city", "value"),
    State("ep-review-site", "value"),
    State("ep-review-product", "value"),
    State("ep-review-year", "value"),
    State("ep-review-status-field", "value"),
    State("ep-review-comment", "value"),
    prevent_initial_call=True,
)
def save_or_confirm_selected_event(
    save_clicks,
    confirm_clicks,
    event_id,
    review_records,
    confirmed,
    company_name,
    event_type,
    country,
    city,
    site_name,
    product_category,
    target_year,
    status,
    review_comment,
):
    trigger = ctx.triggered_id
    records = normalize_review_records(review_records)
    confirmed = confirmed or []

    if trigger == "ep-save-selected-event" and not save_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    if trigger == "ep-confirm-selected-event" and not confirm_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    if not event_id:
        return records, confirmed, "No event selected."

    values = {
        "company_name": company_name or "",
        "event_type": event_type or "",
        "country": country or "",
        "city": city or "",
        "site_name": site_name or "",
        "product_category": product_category or "",
        "target_year": target_year or "",
        "status": status or "",
        "review_comment": review_comment or "",
    }

    if trigger == "ep-confirm-selected-event":
        records = update_review_record(records, event_id, values, mark_confirmed=True)
        if event_id not in confirmed:
            confirmed = confirmed + [event_id]
        return records, confirmed, f"Saved and confirmed {event_id}. Continue until all dropdown events are confirmed."

    records = update_review_record(records, event_id, values, mark_confirmed=False)
    return records, confirmed, f"Saved edits for {event_id}. This record is not confirmed yet."


@callback(
    Output("ep-confirmation-progress", "children"),
    Input("ep-confirmed-events", "data"),
    Input("ep-review-records-store", "data"),
    State("ep-required-events", "data"),
)
def render_confirmation_progress(confirmed, review_records, required):
    confirmed = confirmed or []
    required = required or []
    records = normalize_review_records(review_records)
    saved_ids = {r.get("event_id") for r in records if r.get("edited_in_session")}
    items = []
    for event_id in required:
        done = event_id in confirmed
        saved = event_id in saved_ids
        if done:
            label, color = f"{event_id} ✓ confirmed", "success"
        elif saved:
            label, color = f"{event_id} saved", "info"
        else:
            label, color = f"{event_id} ! pending", "warning"
        items.append(dbc.Badge(label, color=color, className="me-1 mb-1"))
    summary = f"{len(confirmed)}/{len(required)} events confirmed | {len(saved_ids)}/{len(required)} have saved session edits"
    return html.Div([html.Div(summary, className="section-label"), html.Div(items)])


def build_approval_payload(event_id="all_reviewed_events", confirmed=None, force=False, missing=None, reviewed_records=None):
    return {
        "approved": True,
        "approved_event_id": event_id,
        "approved_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "confirmed_events": confirmed or [],
        "force_confirmed": bool(force),
        "missing_individual_confirmations": missing or [],
        "reviewed_records": normalize_review_records(reviewed_records),
        "storage_strategy": "browser_session_store_no_server_database",
    }


def continue_pipeline_after_human_gate(pipeline_state):
    pipeline_state = pipeline_state or initial_state()
    return {
        **pipeline_state,
        "progress": HUMAN_GATE_INDEX + 1,
        "started": True,
        "run_id": pipeline_state.get("run_id") or datetime.utcnow().strftime("%Y%m%d%H%M%S"),
    }


@callback(
    Output("ep-confirm-all-modal", "is_open"),
    Output("ep-missing-events-modal-text", "children"),
    Output("global-human-validation-store", "data", allow_duplicate=True),
    Output("ep-inline-approve-status", "children"),
    Output("ep-pipeline-state", "data", allow_duplicate=True),
    Output("ep-pipeline-timer", "disabled", allow_duplicate=True),
    Output("ep-confirmed-events", "data", allow_duplicate=True),
    Output("ep-review-records-store", "data", allow_duplicate=True),
    Input("ep-confirm-all-reviewed", "n_clicks"),
    Input("ep-force-confirm-all", "n_clicks"),
    Input("ep-cancel-confirm-all-modal", "n_clicks"),
    State("ep-confirmed-events", "data"),
    State("ep-required-events", "data"),
    State("ep-review-records-store", "data"),
    State("ep-pipeline-state", "data"),
    State("ep-confirm-all-modal", "is_open"),
    prevent_initial_call=True,
)
def confirm_all_reviewed(confirm_clicks, force_clicks, cancel_clicks, confirmed, required, review_records, pipeline_state, is_open):
    trigger = ctx.triggered_id
    confirmed = confirmed or []
    required = required or []
    records = normalize_review_records(review_records)
    missing = [event_id for event_id in required if event_id not in confirmed]

    # When the human-review detail panel is first rendered, Dash may initialize
    # newly inserted modal/button components. That initialization must not open
    # the confirmation modal. The modal should open only after an actual click.
    if trigger == "ep-confirm-all-reviewed" and not confirm_clicks:
        return False, "", dash.no_update, "", dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if trigger == "ep-force-confirm-all" and not force_clicks:
        return False, "", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if trigger == "ep-cancel-confirm-all-modal" and not cancel_clicks:
        return False, "", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    if trigger == "ep-cancel-confirm-all-modal":
        return False, "", dash.no_update, "Please review and confirm the remaining events individually.", dash.no_update, dash.no_update, dash.no_update, dash.no_update

    if trigger == "ep-force-confirm-all":
        reviewed_records = mark_records_reviewed(records, required)
        payload = build_approval_payload(
            event_id="all_reviewed_events_force_confirmed",
            confirmed=required,
            force=True,
            missing=missing,
            reviewed_records=reviewed_records,
        )
        return (
            False,
            "",
            payload,
            "All events were saved and confirmed as reviewed, including records that were not individually confirmed.",
            continue_pipeline_after_human_gate(pipeline_state),
            False,
            required,
            reviewed_records,
        )

    if trigger == "ep-confirm-all-reviewed":
        if missing:
            missing_badges = [
                dbc.Badge(event_id, color="warning", text_color="dark", className="me-1 mb-1")
                for event_id in missing
            ]
            modal_text = html.Div(
                [
                    html.Div(f"Missing individual confirmations: {len(missing)}", className="section-label"),
                    html.Div(missing_badges),
                ]
            )
            return True, modal_text, dash.no_update, "Some records are still missing individual confirmation.", dash.no_update, dash.no_update, dash.no_update, dash.no_update

        reviewed_records = mark_records_reviewed(records, required)
        payload = build_approval_payload(event_id="all_reviewed_events", confirmed=confirmed, force=False, missing=[], reviewed_records=reviewed_records)
        return (
            False,
            "",
            payload,
            "All events confirmed. Human validation is completed and the pipeline continues.",
            continue_pipeline_after_human_gate(pipeline_state),
            False,
            confirmed,
            reviewed_records,
        )

    return False if is_open is None else is_open, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output("ep-download-reviewed-events", "data"),
    Input("ep-download-review-csv", "n_clicks"),
    State("global-human-validation-store", "data"),
    prevent_initial_call=True,
)
def download_reviewed_events(n_clicks, approval_data):
    if not n_clicks or not human_gate_approved(approval_data):
        return dash.no_update
    records = normalize_review_records((approval_data or {}).get("reviewed_records"))
    df = pd.DataFrame(records)
    return dcc.send_data_frame(df.to_csv, "validated_company_events_session.csv", index=False)
