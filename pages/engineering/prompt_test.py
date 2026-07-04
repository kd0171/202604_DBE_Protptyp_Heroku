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

FORMAT_GUIDANCE = """These prompts are intentionally general. They do not contain ABF Annual Report source excerpts. For a live demo, copy the relevant text from the sample PDF and paste it into the input area requested by the prompt. The Desired output column shows an example of the expected JSON shape and business meaning, not preloaded source input."""

DESIRED_SCOPE_OUTPUT = """{
  "document_metadata": {
    "document_id": "abf_annual_report_2025",
    "company": "Associated British Foods plc",
    "peer_scope": "ABF Sugar segment",
    "document_type": "annual_report",
    "reporting_year": "2025",
    "fiscal_period_for_dashboard": "2024/25",
    "language": "English",
    "confidence": 0.98
  },
  "relevant_sections": [
    {
      "section_id": "sugar_operating_review",
      "section_title": "Operating review - Sugar",
      "source_page_or_page_range": "34-39",
      "scope": "ABF Sugar",
      "relevant_dashboard_dimensions": ["finance", "risk", "operations", "investment", "sustainability", "regulation"],
      "reason_for_relevance": "This section contains ABF Sugar segment performance, market pressure, restructuring, plant closure, capacity investment and decarbonisation information.",
      "information_types_expected": ["revenue", "adjusted operating profit/loss", "market price pressure", "restructuring", "plant closure", "capacity expansion", "decarbonisation"]
    },
    {
      "section_id": "financial_review_segmental_summary",
      "section_title": "Financial review - Segmental summary",
      "source_page_or_page_range": "44",
      "scope": "ABF Group with Sugar segment data",
      "relevant_dashboard_dimensions": ["finance", "risk"],
      "reason_for_relevance": "This section confirms segment-level Sugar revenue and adjusted operating profit/loss figures.",
      "information_types_expected": ["segment revenue", "adjusted operating profit/loss", "year-on-year change"]
    }
  ],
  "excluded_sections": [
    {"section_title": "Retail / Primark", "reason_for_exclusion": "Not part of the sugar-industry peer comparison."},
    {"section_title": "Grocery", "reason_for_exclusion": "Mostly unrelated branded food businesses unless explicitly linked to sugar."}
  ],
  "scope_warnings": [
    "Do not use ABF Group figures as ABF Sugar figures unless the source explicitly reports Sugar segment data.",
    "Clearly label Vivergo or other closed/disposed operations if they are related to the Sugar segment but reported separately."
  ]
}"""

DESIRED_CHUNKS_OUTPUT = """{
  "chunks": [
    {
      "chunk_id": "abf_2025_regulation_vivergo_001",
      "company_name": "ABF Sugar",
      "business_unit": "Vivergo",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar-related closed operation",
      "category": "regulation",
      "secondary_categories": ["risk", "operations"],
      "topic": "Vivergo bioethanol plant closure",
      "topic_source_text": "Exact original sentence(s) stating that the Vivergo bioethanol plant was decided to be closed.",
      "strategic_signal": "The peer is exposed to regulatory and financial support conditions in bioethanol markets; adverse policy conditions can lead to closure of adjacent assets.",
      "strategic_signal_source_text": "Exact original sentence(s) stating the regulatory / financial reason for the closure.",
      "category_source_text": "Exact original sentence(s) that justify regulation/risk classification.",
      "country": "United Kingdom",
      "city_or_region": "Hull / Humberside",
      "site_name": "Vivergo bioethanol plant",
      "product_category": "bioethanol",
      "target_year": "2025",
      "status": "closure decided",
      "time_horizon": "short-term",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "35",
      "source_section": "Operating review - Sugar",
      "content": "Source-grounded summary of the closure, its regulatory explanation and its relevance for sugar-industry competitive intelligence.",
      "numeric_values": [
        {"metric": "vivergo_sales", "value": 134, "unit": "GBP million", "period": "2025", "source_text": "Exact original source text for this number."},
        {"metric": "vivergo_adjusted_operating_loss", "value": -36, "unit": "GBP million", "period": "2025", "source_text": "Exact original source text for this number."}
      ],
      "dashboard_relevance": ["regulation", "risk", "operations"],
      "confidence": 0.96,
      "limitations": "The strategic interpretation should be separated from directly stated source facts. External policy assessment is outside the document."
    }
  ]
}"""

DESIRED_EVENTS_OUTPUT = """{
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
      "city_or_region": "Hull / Humberside",
      "site_name": "Vivergo bioethanol plant",
      "product_category": "bioethanol",
      "target_year": "2025",
      "status": "closure decided",
      "event_title": "Vivergo bioethanol plant closure decided in 2025",
      "event_summary": "ABF Sugar-related Vivergo was decided for closure after required regulatory and financial support did not materialise.",
      "business_interpretation": "For Nordzucker, this is a regulatory exposure signal for bioethanol and co-product strategies linked to sugar-industry assets.",
      "time_horizon": "short-term",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35",
      "source_section": "Operating review - Sugar",
      "source_text": "Exact original source text supporting the closure and regulatory explanation.",
      "linked_chunk_ids": ["abf_2025_regulation_vivergo_001"],
      "review_comment": "Check whether the source supports both the closure decision and the regulation-linked interpretation. City/region should remain 'Hull / Humberside' only if supported by the pasted source text.",
      "extraction_confidence": 0.96,
      "requires_human_review": true
    }
  ],
  "indicator_records": [
    {
      "indicator_id": "ABF2025_IND_VIVERGO_SALES_001",
      "company_name": "ABF Sugar",
      "business_unit": "Vivergo",
      "metric": "vivergo_sales",
      "value": 134,
      "unit": "GBP million",
      "period": "2025",
      "category": "finance",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35",
      "source_text": "Exact original source text for the sales figure.",
      "linked_chunk_id": "abf_2025_regulation_vivergo_001",
      "requires_human_review": true
    }
  ]
}"""

DESIRED_FINAL_OUTPUT = """{
  "validation_summary": {
    "records_checked": 2,
    "records_supported": 2,
    "records_requiring_revision": 0,
    "overall_status": "passed_with_interpretation_notes"
  },
  "event_validation": [
    {
      "event_id": "ABF2025_EVT_VIVERGO_001",
      "schema_status": "passed",
      "evidence_status": "supported",
      "taxonomy_status": "valid",
      "numeric_values_status": "passed",
      "supported_fields": ["company_name", "business_unit", "event_type", "country", "site_name", "product_category", "target_year", "status", "source_page", "source_text"],
      "unsupported_fields": [],
      "potential_overinterpretations": ["Nordzucker implication is an analyst interpretation and must stay in business_interpretation or review_comment."],
      "recommended_human_action": "confirm",
      "validation_comment": "The closure event is source-supported. Human review should check exact location wording and regulatory interpretation."
    }
  ],
  "indicator_validation": [
    {
      "indicator_id": "ABF2025_IND_VIVERGO_SALES_001",
      "schema_status": "passed",
      "evidence_status": "supported",
      "numeric_value_status": "passed",
      "recommended_human_action": "confirm",
      "validation_comment": "The numeric value is explicitly present in the linked source text."
    }
  ],
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
      "city_or_region": "Hull / Humberside",
      "site_name": "Vivergo bioethanol plant",
      "product_category": "bioethanol",
      "target_year": "2025",
      "status": "closure decided",
      "event_title": "Vivergo bioethanol plant closure decided in 2025",
      "event_summary": "ABF Sugar-related Vivergo was decided for closure after required regulatory and financial support did not materialise.",
      "business_interpretation": "For Nordzucker, this is a regulatory exposure signal for bioethanol and co-product strategies linked to sugar-industry assets.",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35",
      "source_text": "Exact original source text supporting the closure and regulatory explanation.",
      "validation_status": "pending_human_review",
      "review_question": "Does the evidence support the closure decision, regulation-linked classification, location, product category and target year?",
      "recommended_human_action": "confirm",
      "review_comment": "Confirm whether the location should be stored as Hull, Humberside, or both depending on the exact source wording. Keep the Nordzucker implication as interpretation, not as a source fact.",
      "requires_human_review": true
    }
  ]
}"""

PROMPT_CHAINS = [
    {
        "step": "1",
        "title": "Section and scope identification",
        "subtitle": "Find source sections and avoid mixing the target business unit with unrelated group businesses.",
        "pipeline_mapping": "Data Engineering: extract-metadata / parse-pdf",
        "input_hint": "Paste the PDF table of contents, segment overview and relevant section excerpts. For ABF, use the Sugar operating review and Financial Review segmental summary.",
        "prompt": """You are an analyst supporting a competitive intelligence system for a focal company.

Task:
Identify the relevant document scope and source sections for later extraction.

Configuration:
- Focal company: [FOCAL_COMPANY]
- Peer company / document owner: [PEER_COMPANY]
- Relevant peer scope or business unit: [PEER_SCOPE]
- Document title and year: [DOCUMENT_TITLE_AND_YEAR]
- Dashboard dimensions: finance, risk, sustainability, operations, products, regulation, investment, market_context

Input to paste below:
- Table of contents if available
- Segment/business overview
- Any section excerpts that appear relevant for competitive intelligence

Rules:
1. Use only the pasted source text.
2. Prefer sections that are directly about the relevant peer scope/business unit.
3. Do not treat group-level figures as segment-level figures unless the source explicitly states segment-level data.
4. Exclude unrelated business segments unless they provide necessary context for the relevant peer scope.
5. Do not output placeholder or missing-data events. If the pasted source text is insufficient, return relevant_sections: [] and explain what input is missing in scope_warnings.
6. Return JSON only.

Output schema:
{
  "document_metadata": {
    "document_id": "...",
    "company": "...",
    "peer_scope": "...",
    "document_type": "annual_report | sustainability_report | investor_presentation | other",
    "reporting_year": "...",
    "fiscal_period_for_dashboard": "...",
    "language": "...",
    "confidence": 0.0
  },
  "relevant_sections": [
    {
      "section_id": "...",
      "section_title": "...",
      "source_page_or_page_range": "...",
      "scope": "target business unit | group with segment data | unclear",
      "relevant_dashboard_dimensions": ["finance", "risk"],
      "reason_for_relevance": "...",
      "information_types_expected": ["revenue", "operating profit", "market conditions"]
    }
  ],
  "excluded_sections": [
    {"section_title": "...", "reason_for_exclusion": "..."}
  ],
  "scope_warnings": ["..."]
}

SOURCE_TEXT:
[PASTE SOURCE TEXT HERE]""",
        "output": DESIRED_SCOPE_OUTPUT,
    },
    {
        "step": "2",
        "title": "Strategic evidence chunk generation",
        "subtitle": "Create source-grounded semantic chunks that preserve original evidence and can be used for retrieval and extraction.",
        "pipeline_mapping": "Data Engineering: chunk-document / select-passages",
        "input_hint": "Paste the source excerpts selected in Prompt 1. For ABF, paste the exact Vivergo, Sugar performance, Azucarera, Ubombo or British Sugar paragraphs you want to extract from.",
        "prompt": """You are an information extraction assistant for a competitive intelligence system.

Task:
Convert the pasted source text into strategic evidence chunks.

Definition:
A strategic evidence chunk is not a fixed-length text split. It is a self-contained, source-grounded semantic unit that can later be used for retrieval, evidence display and structured event extraction.

Configuration:
- Focal company: [FOCAL_COMPANY]
- Peer company / document owner: [PEER_COMPANY]
- Relevant peer scope or business unit: [PEER_SCOPE]
- Document title and year: [DOCUMENT_TITLE_AND_YEAR]

Allowed dashboard categories:
- finance
- risk
- sustainability
- operations
- products
- regulation
- investment
- market_context

Important rules:
1. Use only the pasted source text.
2. Do not invent facts, values, pages, sites, cities, countries or causes.
3. If a field is not supported by the source, use "unknown" and explain the limitation.
4. Do not output placeholder or missing-data event records.
5. Each chunk must include original source text supporting category, topic and strategic_signal.
6. Include numeric values only if they are explicitly stated.
7. Separate source-supported facts from strategic interpretation.
8. If the text describes a closure of a bioethanol plant, extract the following fields if supported: company_name, business_unit, event topic, country, city_or_region, site_name, product_category, target_year, status.
9. Return JSON only.

Output schema:
{
  "chunks": [
    {
      "chunk_id": "...",
      "company_name": "...",
      "business_unit": "...",
      "parent_company": "...",
      "scope": "target business unit | related closed operation | group | unclear",
      "category": "finance | risk | sustainability | operations | products | regulation | investment | market_context",
      "secondary_categories": ["risk"],
      "topic": "...",
      "topic_source_text": "Exact original text supporting the topic assignment.",
      "strategic_signal": "...",
      "strategic_signal_source_text": "Exact original text supporting the strategic signal.",
      "category_source_text": "Exact original text supporting the category assignment.",
      "country": "...",
      "city_or_region": "...",
      "site_name": "...",
      "product_category": "...",
      "target_year": "...",
      "status": "...",
      "time_horizon": "short-term | medium-term | long-term | unclear",
      "document_type": "annual_report | sustainability_report | investor_presentation | other",
      "reporting_year": "...",
      "fiscal_period_for_dashboard": "...",
      "source_page": "...",
      "source_section": "...",
      "content": "...",
      "numeric_values": [
        {"metric": "...", "value": 0, "unit": "...", "period": "...", "source_text": "..."}
      ],
      "dashboard_relevance": ["finance", "risk"],
      "confidence": 0.0,
      "limitations": "..."
    }
  ]
}

SOURCE_TEXT:
[PASTE SOURCE TEXT HERE]

OPTIONAL_OUTPUT_FROM_PROMPT_1:
[PASTE OUTPUT FROM PROMPT 1 HERE]""",
        "output": DESIRED_CHUNKS_OUTPUT,
    },
    {
        "step": "3",
        "title": "Event and indicator record extraction",
        "subtitle": "Convert evidence chunks into dashboard-ready records that can be reviewed and stored.",
        "pipeline_mapping": "Data Engineering: extract-events-json",
        "input_hint": "Paste the JSON chunks produced by Prompt 2. Do not paste the original PDF text unless it is needed as fallback evidence.",
        "prompt": """You are converting strategic evidence chunks into dashboard-ready event and indicator records for a competitive intelligence dashboard.

Input:
Strategic evidence chunks from the previous prompt chain step.

Task:
Create structured records that can be reviewed by a human analyst and later stored in a relational database.

Important distinction:
- A chunk is a source-grounded semantic evidence unit.
- An event record is a structured business object for dashboard analysis.
- An indicator record is a numeric metric usable in charts or time series.

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

Rules:
1. Use only information contained in the input chunks.
2. Do not create missing-data or placeholder events.
3. Preserve source_page, source_section and source_text.
4. Create event records for business-relevant developments.
5. Create indicator records for numeric metrics.
6. Every record must include evidence text.
7. Every record must have "requires_human_review": true.
8. Keep business_interpretation separate from source-supported facts.
9. If a chunk describes a bioethanol plant closure, prefer event_type = "bioethanol_plant_closure" and preserve company_name, business_unit, country, city_or_region, site_name, product_category, target_year and status.
10. Return JSON only.

Output schema:
{
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
      "source_text": "...",
      "linked_chunk_ids": ["..."],
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
[PASTE OUTPUT FROM PROMPT 2 HERE]""",
        "output": DESIRED_EVENTS_OUTPUT,
    },
    {
        "step": "4",
        "title": "Evidence, schema and business logic verification",
        "subtitle": "Check source support and generate the final Human Review payload.",
        "pipeline_mapping": "Data Engineering: link-evidence / schema-precheck / human-review payload preparation",
        "input_hint": "Paste the chunks from Prompt 2 and the event/indicator records from Prompt 3. The final output should be human_review_payload_records.",
        "prompt": """You are a validation assistant for a competitive intelligence extraction pipeline.

Task:
Verify whether the extracted event and indicator records are supported by the strategic evidence chunks and whether they follow the required schema and taxonomy. Then create the final Human Review payload records.

The Human Review payload is the final presentation output of this prompt chain. It should be understandable as business data: one row per reviewable event, with company, business unit, event type, location/site, product category, target year, status, source evidence and review comment.

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

Validation rules:
1. Check whether each event field is supported by the linked chunk.
2. Check whether each numeric value is explicitly present in the source text.
3. Check whether categories and event types are from the allowed lists.
4. Check whether source_document, source_page and source_text are present.
5. Identify unsupported claims or over-interpretations.
6. Do not create missing-data or placeholder review records.
7. Create final human_review_payload_records only for meaningful, source-supported events.
8. Preserve original source text and clearly separate source-supported facts from business interpretation.
9. For a bioethanol closure record, the Human Review payload should include company_name, business_unit, event_type, country, city_or_region, site_name, product_category, target_year, status and review_comment when supported.
10. Return JSON only.

Output schema:
{
  "validation_summary": {"records_checked": 0, "records_supported": 0, "records_requiring_revision": 0, "overall_status": "passed | passed_with_interpretation_notes | failed"},
  "event_validation": [
    {"event_id": "...", "schema_status": "passed | failed", "evidence_status": "supported | partially_supported | unsupported", "taxonomy_status": "valid | invalid", "numeric_values_status": "passed | failed | not_applicable", "supported_fields": ["..."], "unsupported_fields": ["..."], "potential_overinterpretations": ["..."], "recommended_human_action": "confirm | edit | reject", "validation_comment": "..."}
  ],
  "indicator_validation": [
    {"indicator_id": "...", "schema_status": "passed | failed", "evidence_status": "supported | unsupported", "numeric_value_status": "passed | failed", "recommended_human_action": "confirm | edit | reject", "validation_comment": "..."}
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
      "source_text": "Exact original source text used as evidence.",
      "validation_status": "pending_human_review",
      "review_question": "...",
      "recommended_human_action": "confirm | edit | reject",
      "review_comment": "...",
      "requires_human_review": true
    }
  ]
}

STRATEGIC_EVIDENCE_CHUNKS:
[PASTE OUTPUT FROM PROMPT 2 HERE]

EVENT_AND_INDICATOR_RECORDS:
[PASTE OUTPUT FROM PROMPT 3 HERE]""",
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

Open the PDF and copy the relevant text around the ABF Sugar operating review and Financial Review segment table.

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


def _blank_review_records(count=3):
    return [{key: "" for key, _ in FINAL_TABLE_COLUMNS} for _ in range(count)]


def _records_to_table(records, blank_count=3):
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
                    "Paste the final JSON from Prompt 4. The preview reads only the final human_review_payload_records values and renders them as the table that would be passed to Human Verification. Empty input shows an empty preview table.",
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
                html.P("Use the Sample PDF and copy only the relevant paragraphs into ChatGPT: for example the ABF Sugar operating review, the Vivergo closure paragraph, and the Financial Review segmental summary. The prompts themselves remain general and do not contain source excerpts.", className="home-card-text"),
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
