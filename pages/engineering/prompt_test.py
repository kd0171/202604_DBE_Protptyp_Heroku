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

PROMPT_CHAINS = [
    {
        "step": "1",
        "title": "Section and scope identification",
        "subtitle": "Find the ABF Sugar sections and avoid mixing them with ABF Group or Primark/Grocery data.",
        "pipeline_mapping": "Data Engineering: extract-metadata / parse-pdf",
        "input_hint": "Paste the title page, table of contents, business overview, Sugar operating review and Financial review excerpts from ABF Annual Report 2025.",
        "prompt": """You are an analyst supporting a competitive intelligence system for Nordzucker AG.

Your task is to identify the relevant scope and document sections from an annual report for later information extraction.

Context:
- The focal company is Nordzucker AG.
- The peer company in this document is Associated British Foods plc, but only the ABF Sugar segment is relevant.
- Do not treat Primark, Grocery, Ingredients, Agriculture or the ABF Group as direct sugar-industry peers unless the text explicitly affects ABF Sugar.
- The final dashboard dimensions are:
  finance, risk, sustainability, operations, products, regulation, investment.
- The goal is not to summarize the whole report. The goal is to identify the sections that contain information useful for structured competitive analysis.

Instructions:
1. Identify the document metadata.
2. Identify whether the text belongs to ABF Group overall or specifically to ABF Sugar.
3. List the sections that are relevant for sugar-industry competitive intelligence.
4. For each relevant section, explain which dashboard dimensions it can support.
5. Exclude sections that are mainly about Primark, Grocery, Ingredients or Agriculture unless they are needed for group-level context.
6. Do not invent pages, figures or sections that are not in the provided text.
7. Return JSON only.

Output schema:
{
  "document_metadata": {
    "document_id": "...",
    "company": "...",
    "peer_scope": "...",
    "document_type": "...",
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
      "scope": "ABF Sugar | ABF Group | unclear",
      "relevant_dashboard_dimensions": ["finance", "risk"],
      "reason_for_relevance": "...",
      "information_types_expected": ["revenue", "operating profit", "market conditions"]
    }
  ],
  "excluded_sections": [
    {
      "section_title": "...",
      "reason_for_exclusion": "..."
    }
  ],
  "scope_warnings": ["..."]
}

Text:
[PASTE TEXT HERE]""",
        "output": """{
  "document_metadata": {
    "document_id": "abf_annual_report_2025",
    "company": "Associated British Foods plc",
    "peer_scope": "ABF Sugar segment",
    "document_type": "annual_report",
    "reporting_year": "2025",
    "fiscal_period_for_dashboard": "2024/25",
    "language": "English",
    "confidence": 0.96
  },
  "relevant_sections": [
    {
      "section_id": "sugar_operating_review",
      "section_title": "Operating review - Sugar",
      "source_page_or_page_range": "34-39",
      "scope": "ABF Sugar",
      "relevant_dashboard_dimensions": ["finance", "risk", "operations", "investment", "sustainability"],
      "reason_for_relevance": "This section describes ABF Sugar's business performance, market pressure, restructuring and operational initiatives.",
      "information_types_expected": ["segment revenue", "adjusted operating profit", "pricing pressure", "beet cost", "plant restructuring", "decarbonisation projects"]
    },
    {
      "section_id": "financial_review",
      "section_title": "Financial review",
      "source_page_or_page_range": "44",
      "scope": "ABF Group with segment data",
      "relevant_dashboard_dimensions": ["finance", "risk"],
      "reason_for_relevance": "This section includes segment-level revenue and adjusted operating profit for Sugar.",
      "information_types_expected": ["segment revenue", "adjusted operating profit", "year-on-year change"]
    }
  ],
  "excluded_sections": [
    {
      "section_title": "Retail",
      "reason_for_exclusion": "Primark is not part of the sugar-industry peer comparison."
    }
  ],
  "scope_warnings": [
    "ABF Group figures must not be used as direct ABF Sugar figures unless the source explicitly states segment-level Sugar data."
  ]
}"""
    },
    {
        "step": "2",
        "title": "Strategic evidence chunk generation",
        "subtitle": "Create source-grounded semantic chunks that can be used for retrieval, evidence display and later extraction.",
        "pipeline_mapping": "Data Engineering: chunk-document / select-passages",
        "input_hint": "Paste selected ABF Sugar excerpts, especially Sugar operating review and Financial review segment data.",
        "prompt": """You are an information extraction assistant for a competitive intelligence system in the European sugar industry.

Your task is to convert annual-report text into strategic evidence chunks.

Definition:
A strategic evidence chunk is not a simple fixed-length text chunk. It is a self-contained, source-grounded semantic unit that can later be used for retrieval, evidence display and structured event extraction.

Focal company:
- Nordzucker AG

Peer scope:
- ABF Sugar segment of Associated British Foods plc

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
1. Use only the provided text.
2. Do not invent facts, values, pages or causes.
3. If the text refers to ABF Group overall, mark scope as "ABF Group".
4. If the text refers to ABF Sugar, British Sugar, Azucarera, Illovo Sugar or Vivergo in the context of Sugar, mark scope as "ABF Sugar".
5. Each chunk must be self-contained: someone should understand the business meaning without reading the whole PDF.
6. Include exact source text excerpts.
7. For every category, topic and strategic_signal assignment, include the original source text that supports it.
8. Include numeric values only if they are explicitly stated.
9. Use "unknown" if a field cannot be determined.
10. Return JSON only.

Output schema:
{
  "chunks": [
    {
      "chunk_id": "...",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar | ABF Group | unclear",
      "category": "finance | risk | sustainability | operations | products | regulation | investment | market_context",
      "secondary_categories": ["risk"],
      "topic": "...",
      "topic_source_text": "Exact original text supporting the topic assignment.",
      "strategic_signal": "...",
      "strategic_signal_source_text": "Exact original text supporting the strategic signal.",
      "category_source_text": "Exact original text supporting the category assignment.",
      "time_horizon": "short-term | medium-term | long-term | unclear",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "...",
      "source_section": "...",
      "content": "...",
      "numeric_values": [
        {
          "metric": "...",
          "value": 0,
          "unit": "...",
          "period": "...",
          "source_text": "..."
        }
      ],
      "dashboard_relevance": ["finance", "risk"],
      "confidence": 0.0,
      "limitations": "..."
    }
  ]
}

Text:
[PASTE RELEVANT SECTION TEXT HERE]""",
        "output": """{
  "chunks": [
    {
      "chunk_id": "abf_2025_finance_001",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar",
      "category": "finance",
      "secondary_categories": ["risk"],
      "topic": "Sugar segment profitability collapse",
      "topic_source_text": "Sugar revenue was £2,054m in 2025 and adjusted operating profit was £(2)m, compared with revenue of £2,328m and adjusted operating profit of £213m in 2024.",
      "strategic_signal": "ABF Sugar's profitability deteriorated sharply in 2025, moving from a positive adjusted operating profit in 2024 to a small adjusted operating loss in 2025.",
      "strategic_signal_source_text": "Adjusted operating (loss)/profit £(2)m ... 2024: £213m",
      "category_source_text": "Sugar revenue was £2,054m ... adjusted operating profit was £(2)m",
      "time_horizon": "short-term",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "44",
      "source_section": "Financial review",
      "content": "Sugar revenue was £2,054m in 2025 and adjusted operating profit was £(2)m, compared with revenue of £2,328m and adjusted operating profit of £213m in 2024.",
      "numeric_values": [
        {"metric": "sugar_revenue", "value": 2054, "unit": "GBP million", "period": "2025", "source_text": "Sugar revenue £2,054m"},
        {"metric": "adjusted_operating_profit", "value": -2, "unit": "GBP million", "period": "2025", "source_text": "Adjusted operating (loss)/profit £(2)m"},
        {"metric": "adjusted_operating_profit_previous_year", "value": 213, "unit": "GBP million", "period": "2024", "source_text": "2024: £213m"}
      ],
      "dashboard_relevance": ["finance", "risk"],
      "confidence": 0.95,
      "limitations": "The chunk captures segment performance but does not by itself explain all causal drivers unless the pasted source text includes them."
    }
  ]
}"""
    },
    {
        "step": "3",
        "title": "Event and indicator record extraction",
        "subtitle": "Convert evidence chunks into dashboard-ready records that can be reviewed and stored.",
        "pipeline_mapping": "Data Engineering: extract-events-json",
        "input_hint": "Paste the JSON chunks produced by Prompt 2.",
        "prompt": """You are converting strategic evidence chunks into dashboard-ready event and indicator records for a Nordzucker competitive intelligence dashboard.

Input:
You will receive JSON strategic evidence chunks.

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
2. Do not add causal explanations unless they are supported by the chunk content.
3. Preserve source_page and source_section.
4. Create event records for business-relevant developments.
5. Create indicator records for numeric metrics.
6. Every record must include evidence text.
7. Every record must have "requires_human_review": true.
8. Return JSON only.

Output schema:
{
  "event_records": [
    {
      "event_id": "...",
      "company": "...",
      "parent_company": "...",
      "category": "...",
      "secondary_categories": ["..."],
      "event_type": "...",
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
      "extraction_confidence": 0.0,
      "requires_human_review": true
    }
  ],
  "indicator_records": [
    {
      "indicator_id": "...",
      "company": "...",
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

Strategic evidence chunks:
[PASTE JSON CHUNKS HERE]""",
        "output": """{
  "event_records": [
    {
      "event_id": "ABF2025_EVT_001",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "category": "finance",
      "secondary_categories": ["risk"],
      "event_type": "financial_performance_warning",
      "event_title": "ABF Sugar profitability deteriorated sharply in 2025",
      "event_summary": "ABF Sugar's adjusted operating profit decreased from £213m in 2024 to a £2m adjusted operating loss in 2025.",
      "business_interpretation": "For Nordzucker, this is a peer warning signal: even a large, geographically diversified sugar business can experience rapid margin deterioration under adverse sugar market conditions.",
      "time_horizon": "short-term",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "44",
      "source_section": "Financial review",
      "source_text": "Sugar revenue was £2,054m in 2025 and adjusted operating profit was £(2)m, compared with revenue of £2,328m and adjusted operating profit of £213m in 2024.",
      "linked_chunk_ids": ["abf_2025_finance_001"],
      "extraction_confidence": 0.95,
      "requires_human_review": true
    }
  ],
  "indicator_records": [
    {"indicator_id": "ABF2025_IND_001", "company": "ABF Sugar", "metric": "sugar_revenue", "value": 2054, "unit": "GBP million", "period": "2025", "category": "finance", "source_document": "ABF Annual Report 2025", "source_page": "44", "source_text": "Sugar revenue £2,054m", "linked_chunk_id": "abf_2025_finance_001", "requires_human_review": true},
    {"indicator_id": "ABF2025_IND_002", "company": "ABF Sugar", "metric": "adjusted_operating_profit", "value": -2, "unit": "GBP million", "period": "2025", "category": "finance", "source_document": "ABF Annual Report 2025", "source_page": "44", "source_text": "Adjusted operating (loss)/profit £(2)m", "linked_chunk_id": "abf_2025_finance_001", "requires_human_review": true}
  ]
}"""
    },
    {
        "step": "4",
        "title": "Evidence, schema and business logic verification",
        "subtitle": "Check whether extracted records are supported, schema-valid and ready for human review.",
        "pipeline_mapping": "Data Engineering: link-evidence / schema-precheck",
        "input_hint": "Paste the chunks from Prompt 2 and the event/indicator records from Prompt 3.",
        "prompt": """You are a validation assistant for a competitive intelligence extraction pipeline.

Your task is to verify whether the extracted event and indicator records are supported by the strategic evidence chunks and whether they follow the required schema and taxonomy.

Input:
1. Strategic evidence chunks
2. Event records
3. Indicator records
4. Allowed categories and event types

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
5. Identify unsupported claims, over-interpretations or missing evidence.
6. Do not correct the records directly unless the correction is obvious from the source text.
7. Create a final human-review payload record that an analyst can inspect before database publication.
8. The final human-review payload must preserve the original source text and clearly separate source-supported facts from business interpretation.
9. Return JSON only.

Output schema:
{
  "validation_summary": {"records_checked": 0, "records_supported": 0, "records_requiring_revision": 0, "overall_status": "passed | passed_with_warnings | failed"},
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
      "company": "...",
      "category": "...",
      "secondary_categories": ["..."],
      "event_type": "...",
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
      "requires_human_review": true
    }
  ]
}

Strategic evidence chunks:
[PASTE CHUNKS HERE]

Event records:
[PASTE EVENT RECORDS HERE]

Indicator records:
[PASTE INDICATOR RECORDS HERE]""",
        "output": """{
  "validation_summary": {"records_checked": 3, "records_supported": 3, "records_requiring_revision": 0, "overall_status": "passed"},
  "event_validation": [
    {
      "event_id": "ABF2025_EVT_001",
      "schema_status": "passed",
      "evidence_status": "supported",
      "taxonomy_status": "valid",
      "numeric_values_status": "passed",
      "supported_fields": ["company", "category", "event_type", "event_summary", "fiscal_period_for_dashboard", "source_page", "source_text"],
      "unsupported_fields": [],
      "potential_overinterpretations": ["The phrase 'peer warning signal for Nordzucker' is a business interpretation, not a directly stated source fact. It should remain in business_interpretation, not in source_text."],
      "recommended_human_action": "confirm",
      "validation_comment": "The financial deterioration is directly supported by the source values. The Nordzucker implication is acceptable as a labelled business interpretation."
    }
  ],
  "indicator_validation": [
    {"indicator_id": "ABF2025_IND_001", "schema_status": "passed", "evidence_status": "supported", "numeric_value_status": "passed", "recommended_human_action": "confirm", "validation_comment": "The revenue value is explicitly stated in the source text."},
    {"indicator_id": "ABF2025_IND_002", "schema_status": "passed", "evidence_status": "supported", "numeric_value_status": "passed", "recommended_human_action": "confirm", "validation_comment": "The adjusted operating loss is explicitly stated as £(2)m."}
  ],
  "human_review_payload_records": [
    {
      "review_record_id": "HR_ABF2025_001",
      "event_id": "ABF2025_EVT_001",
      "company": "ABF Sugar",
      "category": "finance",
      "secondary_categories": ["risk"],
      "event_type": "financial_performance_warning",
      "event_title": "ABF Sugar profitability deteriorated sharply in 2025",
      "event_summary": "ABF Sugar's adjusted operating profit decreased from £213m in 2024 to a £2m adjusted operating loss in 2025.",
      "business_interpretation": "For Nordzucker, this is a peer warning signal because even a large sugar business can experience rapid margin deterioration under adverse market conditions.",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "44",
      "source_text": "Sugar revenue was £2,054m in 2025 and adjusted operating profit was £(2)m, compared with revenue of £2,328m and adjusted operating profit of £213m in 2024.",
      "validation_status": "pending_human_review",
      "review_question": "Does the evidence support the event summary and extracted numeric values?",
      "recommended_human_action": "confirm",
      "requires_human_review": true
    }
  ]
}"""
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


def _json_to_pretty(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


def _extract_review_records(data):
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []

    for key in ["human_review_payload_records", "review_payload_records", "human_review_payload"]:
        value = data.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value]

    # Fallback: allow the output of Prompt 3 to be previewed as a human-review-ready record.
    event_records = data.get("event_records")
    if isinstance(event_records, list) and event_records:
        return event_records
    return [data] if any(k in data for k in ["event_id", "event_title", "event_summary", "source_text"]) else []


def _record_to_table_rows(record):
    source = record.get("source_document", "")
    if record.get("source_page"):
        source = f"{source}, p. {record.get('source_page')}" if source else f"p. {record.get('source_page')}"

    fields = [
        ("Review record ID", record.get("review_record_id", "")),
        ("Event ID", record.get("event_id", "")),
        ("Company", record.get("company", "")),
        ("Category", record.get("category", "")),
        ("Secondary categories", record.get("secondary_categories", "")),
        ("Event type", record.get("event_type", "")),
        ("Event title", record.get("event_title", "")),
        ("Event summary", record.get("event_summary", "")),
        ("Business interpretation", record.get("business_interpretation", "")),
        ("Fiscal period", record.get("fiscal_period_for_dashboard", "")),
        ("Source", source),
        ("Evidence / source text", record.get("source_text", "")),
        ("Validation status", record.get("validation_status", "")),
        ("Review question", record.get("review_question", "")),
        ("Recommended human action", record.get("recommended_human_action", "")),
        ("Requires human review", record.get("requires_human_review", "")),
    ]
    return [html.Tr([html.Th(label), html.Td(_json_to_pretty(value))]) for label, value in fields if value not in ["", [], None]]


def final_output_card():
    return dbc.AccordionItem(
        [
            dbc.Alert(
                [
                    html.Strong("Purpose: "),
                    "Paste the final JSON from Prompt 4. The app extracts the human-review payload and renders it as a presentation-friendly table. "
                    "This represents the data passed to Human Verification before verified records are saved to the database.",
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
                                value=PROMPT_CHAINS[-1]["output"],
                                className="prompt-test-final-json-input",
                                spellCheck=False,
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.Div("Human Review table preview", className="section-label"),
                            html.Div(id="pt-final-output-preview"),
                        ],
                        md=6,
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
                dbc.Alert([html.Strong("Purpose of this page. "), "This page does not run a live LLM backend. It displays the prompt chain that can be manually executed in ChatGPT or recorded for the presentation. The desired outputs show the expected JSON shape for the ABF Annual Report 2025 sample."], color="primary", className="py-2 mb-0"),
            ]),
            className="compact-engineering-top",
        ),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Recommended demo material", className="section-label"),
                html.H4("ABF Annual Report 2025", className="prompt-test-card-title"),
                html.P("Use the ABF Sugar operating review and Financial Review segment table as source excerpts. This produces a compact but robust example: ABF Sugar revenue, operating profit deterioration, strategic risk signal and evidence verification.", className="home-card-text"),
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
        return dbc.Alert("Paste the final JSON from Prompt 4 to render the Human Review table.", color="secondary", className="py-2")
    try:
        data = json.loads(value)
    except Exception as exc:
        return dbc.Alert(f"JSON could not be parsed: {exc}", color="warning", className="py-2")

    records = _extract_review_records(data)
    if not records:
        return dbc.Alert("No human_review_payload_records or event-like record was found in the pasted JSON.", color="warning", className="py-2")

    record = records[0]
    return html.Div(
        [
            dbc.Alert(
                [html.Strong("Preview record: "), record.get("event_title") or record.get("event_id") or "Human-review-ready record"],
                color="light",
                className="py-2 mb-2",
            ),
            dbc.Table(
                html.Tbody(_record_to_table_rows(record)),
                bordered=True,
                hover=True,
                size="sm",
                responsive=True,
                className="prompt-test-final-table",
            ),
        ]
    )


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
