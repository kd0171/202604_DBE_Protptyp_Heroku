from __future__ import annotations

from pathlib import Path
import json

import dash
from dash import Input, Output, State, callback, ctx, dcc, html
import dash_bootstrap_components as dbc


dash.register_page(__name__, path="/engineering/prompt-test", name="Prompt Test")

DEFAULT_FILE = "abf-annual-report-2025.pdf.downloadasset.pdf"
APP_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PDF_CANDIDATES = [
    APP_ROOT / "assets" / "compressed_documents" / "04_abf-sugar" / DEFAULT_FILE,
    APP_ROOT / "assets" / "comp" / "04_ABF" / DEFAULT_FILE,
    APP_ROOT / "documents" / "04_abf-sugar" / DEFAULT_FILE,
]
SAMPLE_PDF_PATH = next((path for path in SAMPLE_PDF_CANDIDATES if path.exists()), SAMPLE_PDF_CANDIDATES[0])

FORMAT_GUIDANCE = """These prompts are intentionally general and do not contain ABF Annual Report source excerpts. They demonstrate how the Data Engineering pipeline can be compressed into a short manual prompt chain. The key correction is that Prompt 1 now carries forward selected verbatim source blocks. Therefore Prompt 2 can use the full output of Prompt 1 as its input; the user does not need to paste the PDF excerpt again if Prompt 1 was executed correctly. The Desired output column is an illustrative output-format example, not preloaded source input."""

DESIRED_SCOPE_OUTPUT = """{
  "document_metadata": {
    "document_id": "abf_annual_report_2025",
    "company": "Associated British Foods plc",
    "peer_scope": "ABF Sugar segment or ABF Sugar-related operation",
    "document_type": "annual_report",
    "reporting_year": "2025",
    "fiscal_period_for_dashboard": "2024/25",
    "language": "English",
    "confidence": 0.98
  },
  "source_intake": {
    "upload_pdf": "conceptually registered in the manual demo",
    "register_source": "source registry entry prepared from the pasted page-labelled excerpt",
    "extract_metadata": "company, document type, year, segment scope and page references identified"
  },
  "text_preparation": {
    "parse_pdf": "page-labelled text blocks are treated as extracted PDF text",
    "extract_clean_text": "original wording is preserved for evidence and Human Review",
    "clean_text_requirements": ["preserve original wording", "preserve source_page", "do not rewrite evidence text"]
  },
  "prepared_source_blocks": [
    {
      "block_id": "src_abf_2025_001",
      "source_page": "example: 35",
      "source_section": "example: Operating review - Sugar",
      "scope": "ABF Sugar-related operation",
      "original_text": "Exact source passage copied verbatim from the user-pasted excerpt. This is carried forward to Prompt 2.",
      "why_selected": "Contains a concrete business development and enough evidence for later extraction.",
      "candidate_information_types": ["closure", "regulatory exposure", "financial impact", "site or product information"],
      "possible_dashboard_dimensions": ["regulation", "risk", "operations", "finance"]
    }
  ],
  "extraction_plan": [
    {
      "target_name": "source-supported business event",
      "expected_fields": ["company_name", "business_unit", "event_type", "country", "city_or_region", "site_name", "product_category", "target_year", "status", "extracted_text"]
    }
  ],
  "scope_warnings": [
    "Do not use group-level figures as segment-level figures unless the source explicitly reports segment-level data.",
    "If a location or business unit is not explicit in the source block, mark it as needs_review instead of inventing it."
  ],
  "requires_source_text": false
}"""

DESIRED_CHUNKS_OUTPUT = """{
  "rag_preparation": {
    "chunk_document": "strategic evidence chunks generated from prepared_source_blocks",
    "create_embeddings": "embedding-ready text and metadata fields prepared conceptually",
    "store_vector_db": "metadata fields defined for retrieval, not executed in this manual demo",
    "prepare_retrieval": "chunks can be retrieved by company, category, event_type, source_page and topic"
  },
  "chunks": [
    {
      "chunk_id": "abf_2025_regulation_vivergo_001",
      "company_name": "ABF Sugar",
      "business_unit": "Vivergo",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar-related closed operation",
      "category": "regulation",
      "secondary_categories": ["risk", "operations"],
      "topic": "Bioethanol plant closure",
      "topic_source_text": "Exact original wording that states the closure or stopped production.",
      "strategic_signal": "A sugar-industry peer may face strategic risk when adjacent bioethanol assets depend on regulatory or financial support conditions.",
      "strategic_signal_source_text": "Exact original wording that supports the regulatory or financial support interpretation.",
      "category_source_text": "Exact original wording that justifies regulation/risk classification.",
      "extracted_text": "Longer exact original passage used for Human Review.",
      "country": "United Kingdom",
      "city_or_region": "Humberside / needs_review if only region is stated",
      "site_name": "Vivergo bioethanol plant",
      "product_category": "bioethanol",
      "target_year": "2025",
      "status": "closure decided",
      "time_horizon": "short-term",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "example: 35 or 52",
      "source_section": "source section from Prompt 1",
      "content": "Source-grounded summary plus clearly labelled strategic interpretation.",
      "numeric_values": [
        {"metric": "vivergo_sales", "value": 134, "unit": "GBP million", "period": "2025", "source_text": "Exact original source text supporting this number."}
      ],
      "retrieval_metadata": {
        "embedding_text": "ABF Sugar Vivergo bioethanol closure regulation risk operations + extracted_text",
        "retrieval_keys": ["ABF Sugar", "Vivergo", "bioethanol", "closure", "regulation", "United Kingdom"]
      },
      "dashboard_relevance": ["regulation", "risk", "operations"],
      "confidence": 0.96,
      "limitations": "Keep strategic interpretation separate from directly stated source facts. Location fields should remain needs_review unless directly supported."
    }
  ],
  "missing_input": null
}"""

DESIRED_EVENTS_OUTPUT = """{
  "ie_branch": {
    "select_passages": "selected the most relevant strategic evidence chunk",
    "extract_events_json": "structured closure event and optional numeric indicators created",
    "link_evidence": "each event field is linked back to extracted_text and source_page"
  },
  "event_records": [
    {
      "event_id": "ABF2025_EVT_VIVERGO_001",
      "company_name": "ABF Sugar",
      "business_unit": "Vivergo",
      "parent_company": "Associated British Foods plc",
      "category": "regulation",
      "secondary_categories": ["risk", "operations"],
      "event_type": "bioethanol_plant_closure",
      "country": "United Kingdom",
      "city_or_region": "Humberside / needs_review",
      "site_name": "Vivergo bioethanol plant",
      "product_category": "bioethanol",
      "target_year": "2025",
      "status": "closure decided",
      "event_title": "Vivergo bioethanol plant closure decided in 2025",
      "event_summary": "The ABF Sugar-related Vivergo bioethanol plant was decided for closure after the required regulatory or financial conditions were not met.",
      "business_interpretation": "For Nordzucker, this is a regulatory exposure signal for bioethanol and co-product strategies linked to sugar-industry assets.",
      "time_horizon": "short-term",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "source page from linked chunk",
      "source_section": "source section from linked chunk",
      "extracted_text": "Exact original passage copied from the linked chunk.",
      "source_text": "Shorter exact evidence sentence if useful.",
      "linked_chunk_ids": ["abf_2025_regulation_vivergo_001"],
      "field_evidence_map": {
        "event_type": "exact source wording supporting plant closure",
        "product_category": "exact source wording showing bioethanol",
        "status": "exact source wording showing closure decision",
        "country_or_region": "exact source wording supporting location, or needs_review if partial"
      },
      "review_comment": "Check whether the source supports the closure decision, product category, location wording and regulation-linked classification. Keep Nordzucker implication as interpretation.",
      "extraction_confidence": 0.96,
      "requires_human_review": true
    }
  ],
  "indicator_records": []
}"""

DESIRED_FINAL_OUTPUT = """{
  "human_review_and_validation": {
    "schema_precheck": "category, event_type, required fields and numeric formats checked",
    "human_review": "reviewer receives structured event plus extracted_text evidence",
    "validation_decision": "pending_human_review"
  },
  "validation_summary": {
    "records_checked": 1,
    "records_supported": 1,
    "records_requiring_revision": 0,
    "overall_status": "passed_with_interpretation_notes"
  },
  "event_validation": [
    {
      "event_id": "ABF2025_EVT_VIVERGO_001",
      "schema_status": "passed",
      "evidence_status": "supported",
      "taxonomy_status": "valid",
      "numeric_values_status": "not_applicable",
      "supported_fields": ["company_name", "business_unit", "event_type", "country", "site_name", "product_category", "target_year", "status", "source_page", "extracted_text"],
      "unsupported_fields": [],
      "potential_overinterpretations": ["Nordzucker implication is analyst interpretation and must stay in business_interpretation or review_comment."],
      "recommended_human_action": "confirm",
      "validation_comment": "The closure event is source-supported. Human review should check exact location wording and regulatory interpretation."
    }
  ],
  "indicator_validation": [],
  "human_review_payload_records": [
    {
      "review_record_id": "HR_ABF2025_VIVERGO_001",
      "event_id": "ABF2025_EVT_VIVERGO_001",
      "company_name": "ABF Sugar",
      "business_unit": "Vivergo",
      "parent_company": "Associated British Foods plc",
      "category": "regulation",
      "secondary_categories": ["risk", "operations"],
      "event_type": "bioethanol_plant_closure",
      "country": "United Kingdom",
      "city_or_region": "Humberside / needs_review",
      "site_name": "Vivergo bioethanol plant",
      "product_category": "bioethanol",
      "target_year": "2025",
      "status": "closure decided",
      "event_title": "Vivergo bioethanol plant closure decided in 2025",
      "event_summary": "The ABF Sugar-related Vivergo bioethanol plant was decided for closure after the required regulatory or financial conditions were not met.",
      "business_interpretation": "For Nordzucker, this is a regulatory exposure signal for bioethanol and co-product strategies linked to sugar-industry assets.",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "source page from event record",
      "source_section": "source section from event record",
      "extracted_text": "Exact original passage used by the reviewer to verify the event.",
      "source_text": "Shorter exact evidence sentence if different from extracted_text.",
      "validation_status": "pending_human_review",
      "review_question": "Does the extracted text support the closure decision, regulation-linked classification, location, product category and target year?",
      "recommended_human_action": "confirm",
      "review_comment": "Confirm whether the location should be stored as Humberside, Hull, or needs_review depending on exact source wording. Keep Nordzucker implication as interpretation, not as a source fact.",
      "requires_human_review": true
    }
  ]
}"""

PROMPT_CHAINS = [
    {
        "step": "1",
        "title": "Source intake, metadata and reusable source blocks",
        "subtitle": "Compresses upload-pdf, register-source, extract-metadata, parse-pdf and extract-clean-text into one demo prompt.",
        "pipeline_mapping": "Source Intake: upload-pdf / register-source / extract-metadata; Text Preparation: parse-pdf / extract-clean-text",
        "input_hint": "Paste a concise page-labelled excerpt from the sample PDF. Prompt 1 must preserve selected original source blocks so that Prompt 2 can use its output directly.",
        "prompt": """You are preparing an LLM-assisted competitive intelligence extraction demo for Nordzucker AG.

This prompt corresponds to the early Data Engineering pipeline stages:
- Source Intake: upload-pdf, register-source, extract-metadata
- Text Preparation: parse-pdf, extract-clean-text

The actual PDF upload and PDF parsing are not executed in this manual Prompt Test page. Instead, the pasted page-labelled text is treated as the extracted PDF text.

Default demo configuration:
- Focal company: Nordzucker AG
- Peer company / document owner: Associated British Foods plc
- Relevant peer scope: ABF Sugar and ABF Sugar-related operations, including British Sugar, Azucarera, Illovo Sugar and Vivergo when the source text links them to the Sugar business
- Document type: annual_report
- Document title: ABF Annual Report 2025
- Dashboard dimensions: finance, risk, sustainability, operations, products, regulation, investment, market_context

Task:
Create a source registry, identify the relevant business scope, and prepare reusable source blocks for the next prompt. This step must not only identify sections; it must also carry forward exact original source text.

Instructions:
1. Use only SOURCE_TEXT_TO_ANALYZE and the default demo configuration above.
2. Preserve exact original wording in prepared_source_blocks[].original_text.
3. Each prepared_source_block should be short enough to review but long enough to support extraction: normally one paragraph, one table row, or one coherent page-labelled passage.
4. Prefer source blocks directly related to ABF Sugar or ABF Sugar-related operations, but do not pre-label the final event type.
5. Do not use ABF Group-level figures as ABF Sugar figures unless the text explicitly reports Sugar segment data.
6. If the text discusses Vivergo, treat it as ABF Sugar-related only when the text explicitly links it to Sugar, ABF Sugar, disposed/closed Sugar operations, British Sugar, or the Sugar division.
7. Do not create event records in this step.
8. Do not create missing-data events. If no real source text is pasted, return {"requires_source_text": true, "prepared_source_blocks": []}.
9. Return JSON only.

Output schema:
{
  "document_metadata": {
    "document_id": "...",
    "company": "...",
    "peer_scope": "...",
    "document_type": "annual_report",
    "reporting_year": "...",
    "fiscal_period_for_dashboard": "...",
    "language": "...",
    "confidence": 0.0
  },
  "source_intake": {
    "upload_pdf": "conceptually registered in the manual demo",
    "register_source": "...",
    "extract_metadata": "..."
  },
  "text_preparation": {
    "parse_pdf": "page-labelled source text prepared from pasted excerpt",
    "extract_clean_text": "...",
    "clean_text_requirements": ["preserve original wording", "preserve source_page", "do not rewrite evidence text"]
  },
  "prepared_source_blocks": [
    {
      "block_id": "...",
      "source_page": "...",
      "source_section": "...",
      "scope": "ABF Sugar | ABF Sugar-related operation | ABF Group with segment data | unclear",
      "original_text": "Exact original passage copied verbatim from SOURCE_TEXT_TO_ANALYZE.",
      "why_selected": "...",
      "candidate_information_types": ["event", "indicator", "source evidence"],
      "possible_dashboard_dimensions": ["finance", "risk"]
    }
  ],
  "extraction_plan": [
    {
      "target_name": "...",
      "expected_fields": ["company_name", "business_unit", "event_type", "country", "city_or_region", "site_name", "product_category", "target_year", "status", "extracted_text"]
    }
  ],
  "scope_warnings": ["..."],
  "requires_source_text": false
}

SOURCE_TEXT_TO_ANALYZE:
Paste the selected page-labelled source text here. Do not paste only the output of another prompt here. This field should contain actual report text copied from the PDF.""",
        "output": DESIRED_SCOPE_OUTPUT,
    },
    {
        "step": "2",
        "title": "Strategic evidence chunks and retrieval preparation",
        "subtitle": "Compresses chunk-document, create-embeddings, store-vector-db and prepare-retrieval into one demo prompt.",
        "pipeline_mapping": "RAG branch: chunk-document / create-embeddings / store-vector-db / prepare-retrieval",
        "input_hint": "Paste the full JSON output from Prompt 1. Prompt 2 will use prepared_source_blocks[].original_text as the evidence source.",
        "prompt": """You are preparing retrieval-oriented strategic evidence chunks for an LLM-assisted competitive intelligence pipeline.

This prompt corresponds to the RAG branch of the Data Engineering pipeline:
- chunk-document
- create-embeddings
- store-vector-db
- prepare-retrieval

The Prompt Test page does not actually create embeddings or a vector database. Instead, this prompt prepares strategic evidence chunks and retrieval metadata that would be suitable for those steps.

Default demo configuration:
- Focal company: Nordzucker AG
- Peer company / document owner: Associated British Foods plc
- Relevant peer scope: ABF Sugar and ABF Sugar-related operations, including British Sugar, Azucarera, Illovo Sugar and Vivergo when supported by the source text
- Document type: annual_report
- Document title: ABF Annual Report 2025

Allowed dashboard categories:
- finance
- risk
- sustainability
- operations
- products
- regulation
- investment
- market_context

Task:
Convert the source blocks from Prompt 1 into strategic evidence chunks. Each chunk must be a self-contained, source-grounded semantic unit that can later be used for retrieval, evidence display, event extraction and Human Review.

Important input rule:
- The preferred input is the full JSON output from Prompt 1.
- Use PREPARED_SOURCE_FROM_PROMPT_1.prepared_source_blocks[].original_text as the source text.
- If raw page-labelled text is pasted instead of Prompt 1 output, use that raw text.
- If neither prepared_source_blocks nor raw source text is present, return an empty chunks list and explain that the previous step did not carry forward original source text. Do not create a placeholder event.

Candidate information types to capture when present:
- segment financial performance, margins or profit/loss changes
- plant, site, footprint or capacity changes
- closures, restructuring or discontinued activities
- regulatory or policy exposure affecting operations
- investments in capacity, efficiency, products, co-products or decarbonisation
- sustainability projects with measurable operational impact

Instructions:
1. Use only prepared_source_blocks[].original_text or raw pasted source text.
2. Do not invent facts, values, pages, sites, cities, countries or causes.
3. Each chunk must include extracted_text: the exact original passage copied verbatim from the source block.
4. Also include topic_source_text, strategic_signal_source_text and category_source_text as exact evidence snippets.
5. Include numeric values only if explicitly stated in the source text.
6. Separate source-supported facts from strategic interpretation.
7. If the source describes a bioethanol plant closure, extract these fields when supported: company_name, business_unit, country, city_or_region, site_name, product_category, target_year and status.
8. If the location is partly useful but not directly stated, mark it as "needs_review" rather than inventing it.
9. Return JSON only.

Output schema:
{
  "rag_preparation": {
    "chunk_document": "...",
    "create_embeddings": "conceptual embedding text fields prepared",
    "store_vector_db": "conceptual retrieval metadata prepared",
    "prepare_retrieval": "..."
  },
  "chunks": [
    {
      "chunk_id": "...",
      "company_name": "...",
      "business_unit": "...",
      "parent_company": "...",
      "scope": "ABF Sugar | ABF Sugar-related closed operation | ABF Group with segment data | unclear",
      "category": "finance | risk | sustainability | operations | products | regulation | investment | market_context",
      "secondary_categories": ["risk"],
      "topic": "...",
      "topic_source_text": "Exact original text supporting the topic assignment.",
      "strategic_signal": "...",
      "strategic_signal_source_text": "Exact original text supporting the strategic signal.",
      "category_source_text": "Exact original text supporting the category assignment.",
      "extracted_text": "Exact original passage for Human Review.",
      "country": "...",
      "city_or_region": "...",
      "site_name": "...",
      "product_category": "...",
      "target_year": "...",
      "status": "...",
      "time_horizon": "short-term | medium-term | long-term | unclear",
      "document_type": "annual_report",
      "reporting_year": "...",
      "fiscal_period_for_dashboard": "...",
      "source_page": "...",
      "source_section": "...",
      "content": "Concise source-grounded summary plus clearly labelled strategic interpretation.",
      "numeric_values": [
        {"metric": "...", "value": 0, "unit": "...", "period": "...", "source_text": "Exact original text supporting this number."}
      ],
      "retrieval_metadata": {
        "embedding_text": "company + business_unit + topic + strategic_signal + extracted_text",
        "retrieval_keys": ["..."]
      },
      "dashboard_relevance": ["finance", "risk"],
      "confidence": 0.0,
      "limitations": "..."
    }
  ],
  "missing_input": null
}

PREPARED_SOURCE_FROM_PROMPT_1:
Paste the full JSON output from Prompt 1 here. It should contain prepared_source_blocks with original_text.

OPTIONAL_RAW_SOURCE_TEXT:
If you did not run Prompt 1, paste page-labelled report text here.""",
        "output": DESIRED_CHUNKS_OUTPUT,
    },
    {
        "step": "3",
        "title": "IE event extraction and evidence linking",
        "subtitle": "Compresses select-passages, extract-events-json and link-evidence into one demo prompt.",
        "pipeline_mapping": "IE branch: select-passages / extract-events-json / link-evidence",
        "input_hint": "Paste the full JSON chunks produced by Prompt 2. The output should be meaningful event and indicator records with exact extracted_text evidence.",
        "prompt": """You are converting strategic evidence chunks into dashboard-ready event and indicator records for a Nordzucker competitive intelligence dashboard.

This prompt corresponds to the IE branch of the Data Engineering pipeline:
- select-passages
- extract-events-json
- link-evidence

Input:
Use the strategic evidence chunks created by the previous prompt.

Task:
Select the chunks that are relevant for competitive intelligence, convert them into structured event and indicator records, and link every important field back to exact evidence text.

Important distinction:
- A chunk is a source-grounded semantic evidence unit.
- An event record is a structured business object for dashboard analysis.
- An indicator record is a numeric metric usable in charts or time series.
- extracted_text is the original source passage that will be shown in Human Review.

Allowed primary categories:
- finance
- risk
- sustainability
- operations
- products
- regulation
- investment
- market_context

Allowed event types:
- financial_performance_warning
- revenue_change
- margin_change
- restructuring
- plant_closure
- bioethanol_plant_closure
- capacity_expansion
- decarbonisation_project
- product_portfolio_signal
- regulatory_exposure
- market_price_pressure
- investment_project
- risk_signal
- other

Instructions:
1. Use only information contained in STRATEGIC_EVIDENCE_CHUNKS.
2. Do not create missing-data, placeholder or pipeline-error events.
3. Preserve source_page, source_section, extracted_text and source_text.
4. Create event records for business-relevant developments only.
5. Create indicator records for numeric metrics only when numbers are explicitly stated in the chunks.
6. Every event record must include extracted_text.
7. Every record must have "requires_human_review": true.
8. Keep business_interpretation separate from source-supported facts.
9. If a chunk describes a bioethanol plant closure, use event_type = "bioethanol_plant_closure" and preserve company_name, business_unit, country, city_or_region, site_name, product_category, target_year and status.
10. If city_or_region is useful but not directly supported, mark it as "needs_review" and explain this in review_comment.
11. The output should be close to what the Human Review screen needs, but still unverified.
12. Return JSON only.

Output schema:
{
  "ie_branch": {
    "select_passages": "...",
    "extract_events_json": "...",
    "link_evidence": "..."
  },
  "event_records": [
    {
      "event_id": "...",
      "company_name": "...",
      "business_unit": "...",
      "parent_company": "...",
      "category": "...",
      "secondary_categories": ["..."],
      "event_type": "...",
      "country": "...",
      "city_or_region": "...",
      "site_name": "...",
      "product_category": "...",
      "target_year": "...",
      "status": "...",
      "event_title": "...",
      "event_summary": "...",
      "business_interpretation": "...",
      "time_horizon": "...",
      "fiscal_period_for_dashboard": "...",
      "source_document": "...",
      "source_page": "...",
      "source_section": "...",
      "extracted_text": "Exact original source passage used for Human Review.",
      "source_text": "Shorter exact evidence sentence if useful.",
      "linked_chunk_ids": ["..."],
      "field_evidence_map": {
        "event_type": "exact source text supporting this field",
        "status": "exact source text supporting this field",
        "site_name": "exact source text supporting this field"
      },
      "review_comment": "...",
      "extraction_confidence": 0.0,
      "requires_human_review": true
    }
  ],
  "indicator_records": [
    {
      "indicator_id": "...",
      "company_name": "...",
      "business_unit": "...",
      "metric": "...",
      "value": 0,
      "unit": "...",
      "period": "...",
      "category": "...",
      "source_document": "...",
      "source_page": "...",
      "source_text": "...",
      "linked_chunk_id": "...",
      "requires_human_review": true
    }
  ]
}

STRATEGIC_EVIDENCE_CHUNKS:
Paste the full JSON output from Prompt 2 here.""",
        "output": DESIRED_EVENTS_OUTPUT,
    },
    {
        "step": "4",
        "title": "Schema pre-check and Human Review payload",
        "subtitle": "Compresses schema-precheck and human-review preparation into the final prompt-chain output.",
        "pipeline_mapping": "Human Review & Validation: schema-precheck / human-review",
        "input_hint": "Paste the chunks from Prompt 2 and event/indicator records from Prompt 3. The final output is human_review_payload_records, including extracted_text for manual verification.",
        "prompt": """You are a validation assistant preparing the final Human Review payload for a competitive intelligence extraction pipeline.

This prompt corresponds to the Human Review & Validation phase:
- schema-precheck
- human-review

Task:
Verify whether the extracted event and indicator records are supported by the strategic evidence chunks, whether they follow the required schema and taxonomy, and then create the final human_review_payload_records.

The final output should be understandable as business data. It should look like the record that will be passed to Human Review: one reviewable event per row, including company, business unit, event type, location/site, product category, target year, status, extracted_text evidence and review_comment.

Allowed categories:
- finance
- risk
- sustainability
- operations
- products
- regulation
- investment
- market_context

Allowed event types:
- financial_performance_warning
- revenue_change
- margin_change
- restructuring
- plant_closure
- bioethanol_plant_closure
- capacity_expansion
- decarbonisation_project
- product_portfolio_signal
- regulatory_exposure
- market_price_pressure
- investment_project
- risk_signal
- other

Validation instructions:
1. Check whether each event field is supported by the linked chunk.
2. Check whether extracted_text is present and contains the original source passage needed for human verification.
3. Check whether each numeric value is explicitly present in the source text.
4. Check whether categories and event types are from the allowed lists.
5. Check whether source_document, source_page, source_section and extracted_text are present.
6. Identify unsupported claims or over-interpretations.
7. Do not create missing-data or placeholder review records.
8. Create final human_review_payload_records only for meaningful, source-supported events.
9. Preserve original source text and clearly separate source-supported facts from business interpretation.
10. If a location value is useful but not fully supported by extracted_text, keep the value as "needs_review" or state the uncertainty in review_comment.
11. For a bioethanol closure record, the Human Review payload should include company_name, business_unit, event_type, country, city_or_region, site_name, product_category, target_year, status, extracted_text and review_comment when supported.
12. Return JSON only.

Output schema:
{
  "human_review_and_validation": {
    "schema_precheck": "...",
    "human_review": "...",
    "validation_decision": "pending_human_review"
  },
  "validation_summary": {
    "records_checked": 0,
    "records_supported": 0,
    "records_requiring_revision": 0,
    "overall_status": "passed | passed_with_interpretation_notes | failed"
  },
  "event_validation": [
    {
      "event_id": "...",
      "schema_status": "passed | failed",
      "evidence_status": "supported | partially_supported | unsupported",
      "taxonomy_status": "valid | invalid",
      "numeric_values_status": "passed | failed | not_applicable",
      "supported_fields": ["..."],
      "unsupported_fields": ["..."],
      "potential_overinterpretations": ["..."],
      "recommended_human_action": "confirm | edit | reject",
      "validation_comment": "..."
    }
  ],
  "indicator_validation": [
    {
      "indicator_id": "...",
      "schema_status": "passed | failed",
      "evidence_status": "supported | unsupported",
      "numeric_value_status": "passed | failed",
      "recommended_human_action": "confirm | edit | reject",
      "validation_comment": "..."
    }
  ],
  "human_review_payload_records": [
    {
      "review_record_id": "...",
      "event_id": "...",
      "company_name": "...",
      "business_unit": "...",
      "parent_company": "...",
      "category": "...",
      "secondary_categories": ["..."],
      "event_type": "...",
      "country": "...",
      "city_or_region": "...",
      "site_name": "...",
      "product_category": "...",
      "target_year": "...",
      "status": "...",
      "event_title": "...",
      "event_summary": "...",
      "business_interpretation": "...",
      "fiscal_period_for_dashboard": "...",
      "source_document": "...",
      "source_page": "...",
      "source_section": "...",
      "extracted_text": "Exact original source passage used by the reviewer to verify the event.",
      "source_text": "Shorter exact evidence sentence if different from extracted_text.",
      "validation_status": "pending_human_review",
      "review_question": "Does the extracted text support this event and the extracted fields?",
      "recommended_human_action": "confirm | edit | reject",
      "review_comment": "...",
      "requires_human_review": true
    }
  ]
}

STRATEGIC_EVIDENCE_CHUNKS:
Paste the full JSON output from Prompt 2 here.

EVENT_AND_INDICATOR_RECORDS:
Paste the full JSON output from Prompt 3 here.""",
        "output": DESIRED_FINAL_OUTPUT,
    },
]

TUTORIAL_STEPS = [
    {
        "title": "1. Start the Prompt Test tutorial",
        "text": """
#### Goal

This page shows the prompt chain behind the Data Engineering workflow without requiring a PDF upload.

#### What you can test

Use the **Sample PDF** button to download ABF Annual Report 2025, copy relevant excerpts from the PDF and run the four prompts in ChatGPT or another LLM interface.

#### How to continue

Click **Next** to learn the workflow, or **Skip tutorial** if you already know how to use the page.
""",
        "hint": "This page is designed for a short live demo or screen recording of the LLM prompt chain.",
    },
    {
        "title": "2. Download the sample PDF",
        "media_src": "/assets/tutorial/01_download_sample_pdf.gif",
        "media_alt": "Tutorial GIF showing the Sample PDF button being clicked.",
        "text": """
#### Goal

Download the same official ABF Annual Report 2025 sample PDF used by the Data Engineering View.

#### What to do

Open the PDF and copy a concise page-labelled excerpt that contains concrete business facts. The prompt chain should infer the relevant category, event type and review fields from the evidence rather than from a pre-labelled instruction.

#### Why this matters

Using the same PDF keeps the prompt test, Human Verification records and dashboard examples internally consistent.
""",
        "hint": "The prompt test page does not upload or process the PDF. You manually copy excerpts into the LLM for demonstration purposes.",
    },
    {
        "title": "3. Run the prompts in order",
        "text": """
#### Goal

Follow the four-step prompt chain from source text to validated records.

#### Recommended order

1. Identify section and scope.
2. Generate strategic evidence chunks.
3. Extract event and indicator records.
4. Verify evidence, schema and business logic.

#### Business meaning

This shows how the app's pipeline can be implemented as an auditable LLM-assisted workflow instead of a black-box extraction step.
""",
        "hint": "Each accordion item contains a prompt on the left and the expected JSON-style output on the right.",
    },
    {
        "title": "4. Connect the prompt result to the app",
        "text": """
#### Goal

Understand how the prompt outputs map back to the Data Engineering pipeline.

#### Mapping

Strategic evidence chunks correspond to the RAG-oriented preparation branch. Event and indicator records correspond to the IE branch. Verification output explains why Human Review is required before saving data to the structured database.

#### Final message

The database should receive only records that are source-linked, schema-valid and human-verified.
""",
        "hint": "This completes the prompt test tutorial.",
    },
]


def prompt_pair(item):
    prompt_id = f"pt-prompt-text-{item['step']}"
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Div(f"{item['step']}. Prompt", className="section-label mb-0"),
                            dcc.Clipboard(
                                id=f"pt-copy-prompt-{item['step']}",
                                target_id=prompt_id,
                                title="Copy prompt",
                                className="copy-prompt-button",
                            ),
                        ],
                        className="prompt-test-label-row",
                    ),
                    html.Pre(item["prompt"], id=prompt_id, className="prompt-box prompt-test-pre"),
                ],
                md=6,
            ),
            dbc.Col([html.Div("Desired output", className="section-label"), html.Pre(item["output"], className="json-box prompt-test-pre")], md=6),
        ],
        className="g-3",
    )


def prompt_card(item):
    return dbc.AccordionItem(
        [
            dbc.Alert(
                [html.Strong("Pipeline mapping: "), item["pipeline_mapping"], html.Br(), html.Strong("Recommended input: "), item["input_hint"]],
                color="info",
                className="py-2",
            ),
            prompt_pair(item),
        ],
        title=f"{item['step']}. Prompt: {item['title']}",
        item_id=f"prompt-{item['step']}",
    )


FINAL_TABLE_COLUMNS = [
    ("review_record_id", "Review ID"),
    ("event_id", "Event ID"),
    ("company_name", "Company"),
    ("business_unit", "Business unit"),
    ("event_type", "Event type"),
    ("country", "Country"),
    ("city_or_region", "City / region"),
    ("site_name", "Site"),
    ("product_category", "Product"),
    ("target_year", "Target year"),
    ("status", "Status"),
    ("event_title", "Event title"),
    ("source_page", "Page"),
    ("extracted_text", "Extracted text / evidence"),
    ("review_comment", "Review comment"),
]


def _json_to_pretty(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


def _extract_review_records(data):
    """Return only final Human Review payload records from Prompt 4 output.

    The table preview intentionally does not fall back to event_records or raw
    dictionaries. It should show only the final JSON values that would be passed
    to Human Verification.
    """
    if not isinstance(data, dict):
        return []
    value = data.get("human_review_payload_records")
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []


def _blank_review_records(count=1):
    return [{key: "" for key, _ in FINAL_TABLE_COLUMNS} for _ in range(count)]


def _records_to_table(records, blank_count=1):
    display_records = records if records else _blank_review_records(blank_count)
    header = html.Thead(html.Tr([html.Th(label) for _, label in FINAL_TABLE_COLUMNS]))
    body_rows = []
    for record in display_records:
        body_rows.append(
            html.Tr([
                html.Td(_json_to_pretty(record.get(key, ""))) for key, _ in FINAL_TABLE_COLUMNS
            ])
        )
    return dbc.Table(
        [header, html.Tbody(body_rows)],
        bordered=True,
        hover=True,
        size="sm",
        responsive=True,
        className="prompt-test-final-table prompt-test-final-table-wide",
    )


def final_output_card():
    return dbc.AccordionItem(
        [
            dbc.Alert(
                [
                    html.Strong("Purpose: "),
                    "Paste the final JSON from Prompt 4. The preview reads only the final human_review_payload_records values and renders them as the table that would be passed to Human Verification, including extracted_text evidence. Empty input shows an empty preview table with a minimum row height.",
                ],
                color="success",
                className="py-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Final JSON", className="section-label"),
                            dcc.Textarea(
                                id="pt-final-json-input",
                                value="",
                                placeholder="Paste the final JSON from Prompt 4 here. The table on the right will show only human_review_payload_records.",
                                className="prompt-test-final-json-input",
                                spellCheck=False,
                            ),
                        ],
                        md=5,
                    ),
                    dbc.Col(
                        [
                            html.Div("Human Review table preview", className="section-label"),
                            html.Div(id="pt-final-output-preview", className="prompt-test-final-preview-wrap"),
                        ],
                        md=7,
                    ),
                ],
                className="g-3",
            ),
        ],
        title="Final output preview: Human Review Payload table",
        item_id="final-output-preview",
    )

def tutorial_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(id="pt-tutorial-title")),
            dbc.ModalBody([
                html.Div(id="pt-tutorial-progress", className="tutorial-progress-text"),
                html.Div(id="pt-tutorial-media", className="tutorial-media-placeholder"),
                html.Div(id="pt-tutorial-text", className="tutorial-main-text"),
                html.Div(id="pt-tutorial-hint", className="tutorial-hint-box"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Skip tutorial", id="pt-tutorial-skip", color="secondary", outline=True, className="me-auto", n_clicks=0),
                dbc.Button("Previous", id="pt-tutorial-prev", color="secondary", outline=True, n_clicks=0),
                dbc.Button("Next", id="pt-tutorial-next", color="primary", n_clicks=0),
            ]),
        ],
        id="pt-tutorial-modal",
        centered=True,
        size="xl",
        backdrop="static",
        keyboard=False,
        is_open=True,
    )


def layout():
    return html.Div([
        dcc.Store(id="pt-tutorial-store", storage_type="session", data={"open": True, "step": 0, "completed": False}),
        tutorial_modal(),
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div("Prompt Test", className="compact-page-title"),
                        html.Div("Manual ChatGPT-style test of the LLM prompt chain for ABF Annual Report 2025", className="compact-page-subtitle"),
                    ], md=7),
                    dbc.Col([
                        dbc.Button("Tutorial", id="pt-open-tutorial", color="info", outline=True, size="sm", n_clicks=0, className="me-1"),
                        dbc.Button("Sample PDF", id="pt-download-sample-pdf", color="success", outline=True, size="sm", n_clicks=0),
                        dcc.Download(id="pt-download-sample-pdf-file"),
                    ], md=3, className="compact-tutorial-col sample-pdf-col"),
                    dbc.Col(dbc.Button("Back to Data Engineering", href="/engineering/upload-pipeline", color="secondary", outline=True, size="sm"), md=2, className="text-md-end mt-2 mt-md-0"),
                ], className="align-items-center g-2"),
                html.Hr(className="compact-divider"),
                dbc.Alert([html.Strong("Purpose of this page. "), "This page does not run a live LLM backend. It displays a manually testable prompt chain. ", FORMAT_GUIDANCE], color="primary", className="py-2 mb-0"),
            ]),
            className="compact-engineering-top",
        ),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Recommended demo material", className="section-label"),
                html.H4("ABF Annual Report 2025", className="prompt-test-card-title"),
                html.P("Use the Sample PDF and copy a short page-labelled excerpt into ChatGPT. Choose text that contains concrete business facts, such as performance changes, operational decisions, regulatory exposure, investments or sustainability projects. The prompts remain general and do not contain source excerpts or pre-classified events.", className="home-card-text"),
            ]), className="home-card"), md=6),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Output logic", className="section-label"),
                html.H4("Chunk → Event → Verification", className="prompt-test-card-title"),
                html.P("Prompt 2 creates strategic evidence chunks. Prompt 3 converts them into dashboard-ready event and indicator records. Prompt 4 checks source support, schema validity and human-review readiness.", className="home-card-text"),
            ]), className="home-card"), md=6),
        ], className="chart-row"),
        dbc.Accordion([prompt_card(item) for item in PROMPT_CHAINS] + [final_output_card()], start_collapsed=True, always_open=True, className="prompt-test-accordion"),
    ])


@callback(Output("pt-download-sample-pdf-file", "data"), Input("pt-download-sample-pdf", "n_clicks"), prevent_initial_call=True)
def download_sample_pdf(n_clicks):
    if not n_clicks:
        return dash.no_update
    if not SAMPLE_PDF_PATH.exists():
        return dash.no_update
    return dcc.send_file(str(SAMPLE_PDF_PATH), filename=DEFAULT_FILE)


@callback(Output("pt-final-output-preview", "children"), Input("pt-final-json-input", "value"))
def render_final_output_preview(value):
    if not value or not str(value).strip():
        return _records_to_table([])
    try:
        data = json.loads(value)
    except Exception:
        return _records_to_table([])

    return _records_to_table(_extract_review_records(data))


@callback(
    Output("pt-tutorial-store", "data"),
    Input("pt-open-tutorial", "n_clicks"),
    Input("pt-tutorial-skip", "n_clicks"),
    Input("pt-tutorial-prev", "n_clicks"),
    Input("pt-tutorial-next", "n_clicks"),
    State("pt-tutorial-store", "data"),
    prevent_initial_call=True,
)
def update_tutorial_state(open_clicks, skip_clicks, prev_clicks, next_clicks, store):
    store = store or {"open": True, "step": 0, "completed": False}
    step = int(store.get("step", 0))
    trigger = ctx.triggered_id
    if trigger == "pt-open-tutorial":
        return {"open": True, "step": 0, "completed": False}
    if trigger == "pt-tutorial-skip":
        return {**store, "open": False, "completed": True}
    if trigger == "pt-tutorial-prev":
        return {**store, "open": True, "step": max(step - 1, 0)}
    if trigger == "pt-tutorial-next":
        if step >= len(TUTORIAL_STEPS) - 1:
            return {**store, "open": False, "completed": True}
        return {**store, "open": True, "step": min(step + 1, len(TUTORIAL_STEPS) - 1)}
    return store


@callback(
    Output("pt-tutorial-modal", "is_open"),
    Output("pt-tutorial-title", "children"),
    Output("pt-tutorial-progress", "children"),
    Output("pt-tutorial-media", "children"),
    Output("pt-tutorial-media", "style"),
    Output("pt-tutorial-text", "children"),
    Output("pt-tutorial-hint", "children"),
    Output("pt-tutorial-prev", "disabled"),
    Output("pt-tutorial-next", "children"),
    Input("pt-tutorial-store", "data"),
)
def render_tutorial(store):
    store = store or {"open": True, "step": 0, "completed": False}
    step = min(max(int(store.get("step", 0)), 0), len(TUTORIAL_STEPS) - 1)
    item = TUTORIAL_STEPS[step]
    is_last = step == len(TUTORIAL_STEPS) - 1
    media_children = None
    media_style = {"display": "none"}
    if item.get("media_src"):
        media_children = html.Img(src=item["media_src"], alt=item.get("media_alt", "Tutorial media"), className="tutorial-media-image")
        media_style = {}
    return (
        bool(store.get("open", True)),
        item["title"],
        f"Step {step + 1} of {len(TUTORIAL_STEPS)}",
        media_children,
        media_style,
        dcc.Markdown(item["text"], className="tutorial-markdown"),
        item["hint"],
        step == 0,
        "End tutorial" if is_last else "Next",
    )
