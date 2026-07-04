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

DEMO_SOURCE_EXCERPT = """ABF Annual Report 2025 demo source excerpt for the prompt chain.

[Report page 3 - Our operating businesses]
Sugar ABF Sugar produces a range of sugar and other products from sugar cane and sugar beet in Africa, the UK and Spain. Revenue £2,054m | 11% (2024: £2,328m). Adjusted operating (loss)/profit £(2)m (2024: £213m).

[Report page 35 - Operating review - Sugar]
Sugar sales declined 10% and the segment had an adjusted operating loss of £2m, excluding Vivergo, due to low European sugar prices. In the UK and Spain, sales and profitability declined significantly in 2025 as a result of persistently low European sugar prices and a high cost of beet for the 2023/24 campaign. In our Spanish business, Azucarera, where the cost base has been structurally too high, we have completed restructuring in our northern beet operations to reduce our footprint from three beet facilities to one. We will continue to reduce costs and improve efficiency in our operations. In 2025, we made the decision to close our Vivergo bioethanol plant. This followed the UK Government's decision not to provide the regulatory and financial solution required for Vivergo to operate on a consistently profitable basis. Our Vivergo bioethanol plant had sales of £134m and an adjusted operating loss of £36m in 2025. As a result of the plant's closure, the financial results of Vivergo are within 'disposed and closed operations' and not within the Sugar segment.

[Report page 36 - Operating review - Sugar]
A two-phase factory debottlenecking programme is being invested in, with resulting operational efficiency improvements enabling 20% more cane to be processed and increasing total sugar production by 47,000 tonnes annually over the next five years. These investments are already improving average cane yields which are expected to further increase from 95 to 108 tonnes per hectare over the next five years. The capital investment programme is enhancing reliability and efficiencies across both agricultural and factory operations and will underpin the long-term growth of our Eswatini business.

[Report page 37 - ESG at Sugar]
ABF Sugar Scope 1 and 2 GHG emissions (market-based) decreased by 9% compared to last year and by 23% against its 2018 baseline. These reductions were achieved by continuous improvements to production efficiency, investing in new technology, innovating to use less energy, and fuel-switching to lower-emission sources. In 2025, 60% of total energy consumption came from renewable sources, primarily bagasse, the fibrous by-product of sugar cane crushing. British Sugar's decarbonisation strategy has continued, with projects this year focusing on energy efficiency, steam reduction, renewable resources and fuel switching. The energy reduction project at Bury St Edmunds was delivered at pace. Commissioned in September 2025, it will cut CO2e emissions from the site by 19,500 tonnes per year. At Wissington, construction is now underway on a substantial steam drying project which aims to achieve a reduction of 50,000 tonnes of CO2e per year from 2026.

[Report page 38 - Co-products in Africa]
In Tanzania, demand for potable alcohol (ethanol from molasses) is twice the local supply. A new distillery is being constructed to double Kilombero's production for the domestic market, with an additional 14 million litres per year of high-quality ethanol forecast to be produced at the site. The expansion investment totals £48.2m and also includes a new fertilizer plant. In Eswatini, energy efficiencies resulting from investment in operations have enabled the export of approximately 55GWh of power annually to the national grid, creating a steady revenue stream.

[Report page 44 - Financial review]
The segmental summary reports Sugar revenue of £2,054m in 2025 and £2,328m in 2024. It reports Sugar adjusted operating profit of £(2)m in 2025 and £213m in 2024. Group adjusted operating profit decreased to £1,734m, reflecting lower profitability in Sugar. Operating profit for the Group was £1,483m, after charging exceptional items of £188m, the majority of which are non-cash impairment charges in Sugar.
"""

DEMO_CHUNKS_JSON = """{
  "chunks": [
    {
      "chunk_id": "abf_2025_finance_001",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar",
      "category": "finance",
      "secondary_categories": ["risk"],
      "topic": "Sugar segment profitability collapse",
      "topic_source_text": "Revenue £2,054m | 11% (2024: £2,328m). Adjusted operating (loss)/profit £(2)m (2024: £213m).",
      "strategic_signal": "ABF Sugar moved from strong profitability in 2024 to an adjusted operating loss in 2025, signalling severe margin pressure in the European sugar cycle.",
      "strategic_signal_source_text": "Sugar sales declined 10% and the segment had an adjusted operating loss of £2m, excluding Vivergo, due to low European sugar prices.",
      "category_source_text": "The source explicitly reports revenue, adjusted operating loss/profit and year-on-year financial change for Sugar.",
      "time_horizon": "short-term",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "35 / 44",
      "source_section": "Operating review - Sugar; Financial review",
      "content": "Sugar revenue was £2,054m in 2025, down from £2,328m in 2024. Adjusted operating profit deteriorated from £213m in 2024 to an adjusted operating loss of £2m in 2025.",
      "numeric_values": [
        {"metric": "sugar_revenue", "value": 2054, "unit": "GBP million", "period": "2025", "source_text": "Revenue £2,054m"},
        {"metric": "sugar_revenue_previous_year", "value": 2328, "unit": "GBP million", "period": "2024", "source_text": "2024: £2,328m"},
        {"metric": "adjusted_operating_profit", "value": -2, "unit": "GBP million", "period": "2025", "source_text": "Adjusted operating (loss)/profit £(2)m"},
        {"metric": "adjusted_operating_profit_previous_year", "value": 213, "unit": "GBP million", "period": "2024", "source_text": "2024: £213m"}
      ],
      "dashboard_relevance": ["finance", "risk"],
      "confidence": 0.97,
      "limitations": "The causal explanation is limited to low European sugar prices and beet cost pressure explicitly stated in the source."
    },
    {
      "chunk_id": "abf_2025_operations_azucarera_001",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar",
      "category": "operations",
      "secondary_categories": ["risk", "investment"],
      "topic": "Azucarera restructuring in Spain",
      "topic_source_text": "In our Spanish business, Azucarera, where the cost base has been structurally too high, we have completed restructuring in our northern beet operations to reduce our footprint from three beet facilities to one.",
      "strategic_signal": "ABF Sugar is reducing structurally high-cost Spanish beet processing capacity to protect profitability under low-price conditions.",
      "strategic_signal_source_text": "Sales and profitability declined significantly in 2025 as a result of persistently low European sugar prices and a high cost of beet ... Azucarera ... reduce our footprint from three beet facilities to one.",
      "category_source_text": "The source describes factory footprint reduction and operational restructuring.",
      "time_horizon": "short-term",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "35",
      "source_section": "Operating review - Sugar",
      "content": "Azucarera completed restructuring in northern beet operations, reducing the footprint from three beet facilities to one because the cost base was structurally too high under low European sugar prices and high beet costs.",
      "numeric_values": [
        {"metric": "beet_facilities_before", "value": 3, "unit": "facilities", "period": "2025", "source_text": "from three beet facilities"},
        {"metric": "beet_facilities_after", "value": 1, "unit": "facility", "period": "2025", "source_text": "to one"}
      ],
      "dashboard_relevance": ["operations", "risk", "investment"],
      "confidence": 0.95,
      "limitations": "The excerpt does not specify the full implementation timetable beyond completion of the northern beet restructuring."
    },
    {
      "chunk_id": "abf_2025_regulation_vivergo_001",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar",
      "category": "regulation",
      "secondary_categories": ["risk", "operations"],
      "topic": "Vivergo bioethanol closure due to regulatory and financial uncertainty",
      "topic_source_text": "In 2025, we made the decision to close our Vivergo bioethanol plant. This followed the UK Government's decision not to provide the regulatory and financial solution required for Vivergo to operate on a consistently profitable basis.",
      "strategic_signal": "ABF Sugar is exposed to regulatory decisions in bioethanol markets, and adverse policy conditions can trigger plant closure despite prior investment.",
      "strategic_signal_source_text": "The UK Government's decision not to provide the regulatory and financial solution required for Vivergo to operate on a consistently profitable basis.",
      "category_source_text": "The source explicitly links the closure to government regulatory and financial support conditions.",
      "time_horizon": "short-term",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "35",
      "source_section": "Operating review - Sugar",
      "content": "ABF decided to close Vivergo after the UK Government did not provide the regulatory and financial solution needed for consistent profitability. Vivergo had sales of £134m and an adjusted operating loss of £36m in 2025.",
      "numeric_values": [
        {"metric": "vivergo_sales", "value": 134, "unit": "GBP million", "period": "2025", "source_text": "Vivergo bioethanol plant had sales of £134m"},
        {"metric": "vivergo_adjusted_operating_loss", "value": -36, "unit": "GBP million", "period": "2025", "source_text": "an adjusted operating loss of £36m in 2025"}
      ],
      "dashboard_relevance": ["regulation", "risk", "operations"],
      "confidence": 0.96,
      "limitations": "The excerpt provides ABF's stated view of the regulatory cause; external policy assessment is outside the source."
    },
    {
      "chunk_id": "abf_2025_investment_ubombo_001",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar",
      "category": "investment",
      "secondary_categories": ["operations"],
      "topic": "Ubombo Sugar capacity and efficiency investment",
      "topic_source_text": "A two-phase factory debottlenecking programme is being invested in ... enabling 20% more cane to be processed and increasing total sugar production by 47,000 tonnes annually over the next five years.",
      "strategic_signal": "ABF Sugar is investing in African capacity and agricultural efficiency to support long-term growth outside the pressured European market.",
      "strategic_signal_source_text": "Driving sustainable long-term growth in Africa is key to ABF Sugar's strategy ... investing in our African markets to enhance production capacity, operational effectiveness and agricultural practices.",
      "category_source_text": "The source describes an investment programme, capacity increase and operational efficiency improvements.",
      "time_horizon": "medium-term",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "36",
      "source_section": "Operating review - Sugar",
      "content": "A two-phase debottlenecking programme at Ubombo Sugar in Eswatini is expected to enable 20% more cane processing and increase sugar production by 47,000 tonnes annually over the next five years.",
      "numeric_values": [
        {"metric": "additional_cane_processing", "value": 20, "unit": "percent", "period": "next five years", "source_text": "enabling 20% more cane to be processed"},
        {"metric": "additional_sugar_production", "value": 47000, "unit": "tonnes annually", "period": "next five years", "source_text": "increasing total sugar production by 47,000 tonnes annually"}
      ],
      "dashboard_relevance": ["investment", "operations"],
      "confidence": 0.95,
      "limitations": "Investment amount for this specific debottlenecking programme is not provided in the excerpt."
    },
    {
      "chunk_id": "abf_2025_sustainability_british_sugar_001",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "scope": "ABF Sugar",
      "category": "sustainability",
      "secondary_categories": ["investment", "operations"],
      "topic": "British Sugar decarbonisation projects",
      "topic_source_text": "British Sugar's decarbonisation strategy has continued, with projects this year focusing on energy efficiency, steam reduction, renewable resources and fuel switching.",
      "strategic_signal": "ABF Sugar is reducing emissions through factory-level energy efficiency and steam reduction projects with quantified annual CO2e savings.",
      "strategic_signal_source_text": "The energy reduction project at Bury St Edmunds ... will cut CO2e emissions from the site by 19,500 tonnes per year. At Wissington ... aims to achieve a reduction of 50,000 tonnes of CO2e per year from 2026.",
      "category_source_text": "The source reports GHG emissions reduction and decarbonisation projects.",
      "time_horizon": "medium-term",
      "document_type": "annual_report",
      "reporting_year": "2025",
      "fiscal_period_for_dashboard": "2024/25",
      "source_page": "37",
      "source_section": "ESG at Sugar",
      "content": "ABF Sugar Scope 1 and 2 market-based emissions decreased by 9% year-on-year and 23% against the 2018 baseline. British Sugar projects at Bury St Edmunds and Wissington are expected to cut 19,500 and 50,000 tonnes of CO2e per year respectively.",
      "numeric_values": [
        {"metric": "scope_1_2_emissions_reduction_yoy", "value": 9, "unit": "percent", "period": "2025", "source_text": "decreased by 9% compared to last year"},
        {"metric": "scope_1_2_emissions_reduction_vs_baseline", "value": 23, "unit": "percent", "period": "against 2018 baseline", "source_text": "by 23% against its 2018 baseline"},
        {"metric": "bury_st_edmunds_co2e_reduction", "value": 19500, "unit": "tonnes CO2e per year", "period": "from September 2025", "source_text": "will cut CO2e emissions from the site by 19,500 tonnes per year"},
        {"metric": "wissington_co2e_reduction_target", "value": 50000, "unit": "tonnes CO2e per year", "period": "from 2026", "source_text": "aims to achieve a reduction of 50,000 tonnes of CO2e per year from 2026"}
      ],
      "dashboard_relevance": ["sustainability", "investment", "operations"],
      "confidence": 0.96,
      "limitations": "The excerpt does not provide project costs or payback periods."
    }
  ]
}"""

DEMO_EVENTS_JSON = """{
  "event_records": [
    {
      "event_id": "ABF2025_EVT_001",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "category": "finance",
      "secondary_categories": ["risk"],
      "event_type": "financial_performance_warning",
      "event_title": "ABF Sugar profitability deteriorated sharply in 2025",
      "event_summary": "ABF Sugar revenue declined to £2,054m and adjusted operating profit fell from £213m in 2024 to a £2m adjusted operating loss in 2025.",
      "business_interpretation": "For Nordzucker, this is a peer warning signal that European sugar price pressure and beet cost exposure can rapidly turn a profitable sugar segment into a loss-making one.",
      "time_horizon": "short-term",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35 / 44",
      "source_section": "Operating review - Sugar; Financial review",
      "source_text": "Revenue £2,054m | 11% (2024: £2,328m). Adjusted operating (loss)/profit £(2)m (2024: £213m). Sugar sales declined 10% and the segment had an adjusted operating loss of £2m, excluding Vivergo, due to low European sugar prices.",
      "linked_chunk_ids": ["abf_2025_finance_001"],
      "extraction_confidence": 0.97,
      "requires_human_review": true
    },
    {
      "event_id": "ABF2025_EVT_002",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "category": "operations",
      "secondary_categories": ["risk", "investment"],
      "event_type": "restructuring",
      "event_title": "Azucarera reduced northern beet operations from three facilities to one",
      "event_summary": "ABF Sugar completed restructuring in Azucarera's northern beet operations, reducing the footprint from three beet facilities to one.",
      "business_interpretation": "The restructuring shows how peers may respond to low-price sugar cycles by closing or consolidating structurally high-cost beet processing capacity.",
      "time_horizon": "short-term",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35",
      "source_section": "Operating review - Sugar",
      "source_text": "In our Spanish business, Azucarera, where the cost base has been structurally too high, we have completed restructuring in our northern beet operations to reduce our footprint from three beet facilities to one.",
      "linked_chunk_ids": ["abf_2025_operations_azucarera_001"],
      "extraction_confidence": 0.95,
      "requires_human_review": true
    },
    {
      "event_id": "ABF2025_EVT_003",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "category": "regulation",
      "secondary_categories": ["risk", "operations"],
      "event_type": "plant_closure",
      "event_title": "Vivergo bioethanol plant closed after regulatory and financial support did not materialise",
      "event_summary": "ABF Sugar decided to close Vivergo after the UK Government did not provide the regulatory and financial solution required for consistent profitability.",
      "business_interpretation": "This record highlights regulatory exposure in bioethanol and co-product markets, where policy design can affect the viability of adjacent sugar-industry assets.",
      "time_horizon": "short-term",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35",
      "source_section": "Operating review - Sugar",
      "source_text": "In 2025, we made the decision to close our Vivergo bioethanol plant. This followed the UK Government's decision not to provide the regulatory and financial solution required for Vivergo to operate on a consistently profitable basis.",
      "linked_chunk_ids": ["abf_2025_regulation_vivergo_001"],
      "extraction_confidence": 0.96,
      "requires_human_review": true
    },
    {
      "event_id": "ABF2025_EVT_004",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "category": "investment",
      "secondary_categories": ["operations"],
      "event_type": "capacity_expansion",
      "event_title": "Ubombo Sugar investment expected to add 47,000 tonnes of annual sugar production",
      "event_summary": "A two-phase debottlenecking programme at Ubombo Sugar is expected to enable 20% more cane processing and add 47,000 tonnes of annual sugar production over the next five years.",
      "business_interpretation": "ABF Sugar is using African capacity investments to build growth outside the pressured European beet market.",
      "time_horizon": "medium-term",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "36",
      "source_section": "Operating review - Sugar",
      "source_text": "A two-phase factory debottlenecking programme is being invested in ... enabling 20% more cane to be processed and increasing total sugar production by 47,000 tonnes annually over the next five years.",
      "linked_chunk_ids": ["abf_2025_investment_ubombo_001"],
      "extraction_confidence": 0.95,
      "requires_human_review": true
    },
    {
      "event_id": "ABF2025_EVT_005",
      "company": "ABF Sugar",
      "parent_company": "Associated British Foods plc",
      "category": "sustainability",
      "secondary_categories": ["investment", "operations"],
      "event_type": "decarbonisation_project",
      "event_title": "British Sugar projects target quantified CO2e reductions",
      "event_summary": "British Sugar's Bury St Edmunds energy reduction project will cut 19,500 tonnes of CO2e per year, while the Wissington steam drying project aims to reduce 50,000 tonnes of CO2e per year from 2026.",
      "business_interpretation": "The record gives Nordzucker a concrete peer benchmark for factory-level decarbonisation projects with quantified annual emissions-reduction effects.",
      "time_horizon": "medium-term",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "37",
      "source_section": "ESG at Sugar",
      "source_text": "The energy reduction project at Bury St Edmunds ... will cut CO2e emissions from the site by 19,500 tonnes per year. At Wissington ... aims to achieve a reduction of 50,000 tonnes of CO2e per year from 2026.",
      "linked_chunk_ids": ["abf_2025_sustainability_british_sugar_001"],
      "extraction_confidence": 0.96,
      "requires_human_review": true
    }
  ],
  "indicator_records": [
    {"indicator_id": "ABF2025_IND_001", "company": "ABF Sugar", "metric": "sugar_revenue", "value": 2054, "unit": "GBP million", "period": "2025", "category": "finance", "source_document": "ABF Annual Report 2025", "source_page": "35 / 44", "source_text": "Revenue £2,054m", "linked_chunk_id": "abf_2025_finance_001", "requires_human_review": true},
    {"indicator_id": "ABF2025_IND_002", "company": "ABF Sugar", "metric": "adjusted_operating_profit", "value": -2, "unit": "GBP million", "period": "2025", "category": "finance", "source_document": "ABF Annual Report 2025", "source_page": "35 / 44", "source_text": "Adjusted operating (loss)/profit £(2)m", "linked_chunk_id": "abf_2025_finance_001", "requires_human_review": true},
    {"indicator_id": "ABF2025_IND_003", "company": "ABF Sugar", "metric": "additional_sugar_production_ubombo", "value": 47000, "unit": "tonnes annually", "period": "next five years", "category": "investment", "source_document": "ABF Annual Report 2025", "source_page": "36", "source_text": "increasing total sugar production by 47,000 tonnes annually", "linked_chunk_id": "abf_2025_investment_ubombo_001", "requires_human_review": true},
    {"indicator_id": "ABF2025_IND_004", "company": "ABF Sugar", "metric": "bury_st_edmunds_co2e_reduction", "value": 19500, "unit": "tonnes CO2e per year", "period": "from September 2025", "category": "sustainability", "source_document": "ABF Annual Report 2025", "source_page": "37", "source_text": "will cut CO2e emissions from the site by 19,500 tonnes per year", "linked_chunk_id": "abf_2025_sustainability_british_sugar_001", "requires_human_review": true},
    {"indicator_id": "ABF2025_IND_005", "company": "ABF Sugar", "metric": "wissington_co2e_reduction_target", "value": 50000, "unit": "tonnes CO2e per year", "period": "from 2026", "category": "sustainability", "source_document": "ABF Annual Report 2025", "source_page": "37", "source_text": "aims to achieve a reduction of 50,000 tonnes of CO2e per year from 2026", "linked_chunk_id": "abf_2025_sustainability_british_sugar_001", "requires_human_review": true}
  ]
}"""

DEMO_FINAL_JSON = """{
  "validation_summary": {
    "records_checked": 10,
    "records_supported": 10,
    "records_requiring_revision": 0,
    "overall_status": "passed_with_interpretation_notes"
  },
  "event_validation": [
    {
      "event_id": "ABF2025_EVT_001",
      "schema_status": "passed",
      "evidence_status": "supported",
      "taxonomy_status": "valid",
      "numeric_values_status": "passed",
      "supported_fields": ["company", "category", "event_type", "event_summary", "source_page", "source_text"],
      "unsupported_fields": [],
      "potential_overinterpretations": ["The Nordzucker implication is an analyst interpretation and must remain in business_interpretation."],
      "recommended_human_action": "confirm",
      "validation_comment": "The revenue and adjusted operating profit figures are explicitly supported by the source text."
    }
  ],
  "indicator_validation": [
    {
      "indicator_id": "ABF2025_IND_001",
      "schema_status": "passed",
      "evidence_status": "supported",
      "numeric_value_status": "passed",
      "recommended_human_action": "confirm",
      "validation_comment": "The revenue value is explicitly present in the source text."
    }
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
      "event_summary": "ABF Sugar revenue declined to £2,054m and adjusted operating profit fell from £213m in 2024 to a £2m adjusted operating loss in 2025.",
      "business_interpretation": "For Nordzucker, this is a peer warning signal that European sugar price pressure and beet cost exposure can rapidly turn a profitable sugar segment into a loss-making one.",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35 / 44",
      "source_text": "Revenue £2,054m | 11% (2024: £2,328m). Adjusted operating (loss)/profit £(2)m (2024: £213m). Sugar sales declined 10% and the segment had an adjusted operating loss of £2m, excluding Vivergo, due to low European sugar prices.",
      "validation_status": "pending_human_review",
      "review_question": "Does the evidence support the extracted revenue, profit change and finance/risk classification?",
      "recommended_human_action": "confirm",
      "requires_human_review": true
    },
    {
      "review_record_id": "HR_ABF2025_002",
      "event_id": "ABF2025_EVT_002",
      "company": "ABF Sugar",
      "category": "operations",
      "secondary_categories": ["risk", "investment"],
      "event_type": "restructuring",
      "event_title": "Azucarera reduced northern beet operations from three facilities to one",
      "event_summary": "ABF Sugar completed restructuring in Azucarera's northern beet operations, reducing the footprint from three beet facilities to one.",
      "business_interpretation": "The restructuring shows how peers may respond to low-price sugar cycles by closing or consolidating structurally high-cost beet processing capacity.",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35",
      "source_text": "In our Spanish business, Azucarera, where the cost base has been structurally too high, we have completed restructuring in our northern beet operations to reduce our footprint from three beet facilities to one.",
      "validation_status": "pending_human_review",
      "review_question": "Does the source support the restructuring event and the three-to-one facility reduction?",
      "recommended_human_action": "confirm",
      "requires_human_review": true
    },
    {
      "review_record_id": "HR_ABF2025_003",
      "event_id": "ABF2025_EVT_003",
      "company": "ABF Sugar",
      "category": "regulation",
      "secondary_categories": ["risk", "operations"],
      "event_type": "plant_closure",
      "event_title": "Vivergo bioethanol plant closed after regulatory and financial support did not materialise",
      "event_summary": "ABF Sugar decided to close Vivergo after the UK Government did not provide the regulatory and financial solution required for consistent profitability.",
      "business_interpretation": "This highlights regulatory exposure in bioethanol and co-product markets, where policy design can affect the viability of adjacent sugar-industry assets.",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "35",
      "source_text": "In 2025, we made the decision to close our Vivergo bioethanol plant. This followed the UK Government's decision not to provide the regulatory and financial solution required for Vivergo to operate on a consistently profitable basis.",
      "validation_status": "pending_human_review",
      "review_question": "Does the evidence support classifying this as a regulation-linked plant closure?",
      "recommended_human_action": "confirm",
      "requires_human_review": true
    },
    {
      "review_record_id": "HR_ABF2025_004",
      "event_id": "ABF2025_EVT_004",
      "company": "ABF Sugar",
      "category": "investment",
      "secondary_categories": ["operations"],
      "event_type": "capacity_expansion",
      "event_title": "Ubombo Sugar investment expected to add 47,000 tonnes of annual sugar production",
      "event_summary": "A two-phase debottlenecking programme at Ubombo Sugar is expected to enable 20% more cane processing and add 47,000 tonnes of annual sugar production over the next five years.",
      "business_interpretation": "ABF Sugar is using African capacity investments to build growth outside the pressured European beet market.",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "36",
      "source_text": "A two-phase factory debottlenecking programme is being invested in ... enabling 20% more cane to be processed and increasing total sugar production by 47,000 tonnes annually over the next five years.",
      "validation_status": "pending_human_review",
      "review_question": "Does the source support the capacity expansion metrics and investment classification?",
      "recommended_human_action": "confirm",
      "requires_human_review": true
    },
    {
      "review_record_id": "HR_ABF2025_005",
      "event_id": "ABF2025_EVT_005",
      "company": "ABF Sugar",
      "category": "sustainability",
      "secondary_categories": ["investment", "operations"],
      "event_type": "decarbonisation_project",
      "event_title": "British Sugar projects target quantified CO2e reductions",
      "event_summary": "British Sugar's Bury St Edmunds energy reduction project will cut 19,500 tonnes of CO2e per year, while the Wissington steam drying project aims to reduce 50,000 tonnes of CO2e per year from 2026.",
      "business_interpretation": "The record gives Nordzucker a concrete peer benchmark for factory-level decarbonisation projects with quantified annual emissions-reduction effects.",
      "fiscal_period_for_dashboard": "2024/25",
      "source_document": "ABF Annual Report 2025",
      "source_page": "37",
      "source_text": "The energy reduction project at Bury St Edmunds ... will cut CO2e emissions from the site by 19,500 tonnes per year. At Wissington ... aims to achieve a reduction of 50,000 tonnes of CO2e per year from 2026.",
      "validation_status": "pending_human_review",
      "review_question": "Does the evidence support the two quantified decarbonisation figures and sustainability classification?",
      "recommended_human_action": "confirm",
      "requires_human_review": true
    }
  ]
}"""

PROMPT_CHAINS = [
    {
        "step": "1",
        "title": "Section and scope identification",
        "subtitle": "Find ABF Sugar source sections and avoid mixing them with unrelated ABF Group businesses.",
        "pipeline_mapping": "Data Engineering: extract-metadata / parse-pdf",
        "input_hint": "This prompt is self-contained for the demo. It already includes short ABF Annual Report 2025 source excerpts.",
        "prompt": f"""You are an analyst supporting a competitive intelligence system for Nordzucker AG.

Task:
Identify the relevant document scope and source sections for later extraction. The final peer scope is ABF Sugar, not the full ABF Group.

Context:
- Focal company: Nordzucker AG.
- Peer document: Associated British Foods plc Annual Report 2025.
- Relevant peer scope: ABF Sugar segment.
- Exclude Primark, Grocery, Ingredients and Agriculture unless they provide group-level context for Sugar.
- Dashboard dimensions: finance, risk, sustainability, operations, products, regulation, investment, market_context.

Rules:
1. Use only the provided demo source excerpt.
2. Prefer concrete ABF Sugar sections over broad group-level sections.
3. Do not output placeholder or missing-data error records.
4. Return JSON only.

Output schema:
{{
  "document_metadata": {{
    "document_id": "...",
    "company": "...",
    "peer_scope": "...",
    "document_type": "...",
    "reporting_year": "...",
    "fiscal_period_for_dashboard": "...",
    "language": "...",
    "confidence": 0.0
  }},
  "relevant_sections": [
    {{
      "section_id": "...",
      "section_title": "...",
      "source_page_or_page_range": "...",
      "scope": "ABF Sugar | ABF Group with Sugar segment data | unclear",
      "relevant_dashboard_dimensions": ["finance", "risk"],
      "reason_for_relevance": "...",
      "information_types_expected": ["revenue", "operating profit", "market conditions"]
    }}
  ],
  "excluded_sections": [
    {{"section_title": "...", "reason_for_exclusion": "..."}}
  ],
  "scope_warnings": ["..."]
}}

DEMO_SOURCE_EXCERPT:
{DEMO_SOURCE_EXCERPT}""",
        "output": """{
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
      "reason_for_relevance": "This is the core ABF Sugar section. It contains segment revenue, profit deterioration, Azucarera restructuring, Vivergo closure, African capacity investment and British Sugar decarbonisation projects.",
      "information_types_expected": ["revenue", "adjusted operating loss", "market price pressure", "restructuring", "plant closure", "capacity expansion", "decarbonisation"]
    },
    {
      "section_id": "financial_review_segmental_summary",
      "section_title": "Financial review - Segmental summary",
      "source_page_or_page_range": "44",
      "scope": "ABF Group with Sugar segment data",
      "relevant_dashboard_dimensions": ["finance", "risk"],
      "reason_for_relevance": "This section confirms Sugar segment revenue and adjusted operating profit for 2025 and 2024, enabling dashboard-ready financial indicators.",
      "information_types_expected": ["segment revenue", "adjusted operating profit", "year-on-year change"]
    }
  ],
  "excluded_sections": [
    {"section_title": "Retail / Primark", "reason_for_exclusion": "Not part of the sugar-industry peer comparison."},
    {"section_title": "Grocery", "reason_for_exclusion": "Mostly unrelated branded food businesses; only Silver Spoon may be relevant if explicitly linked to Sugar."},
    {"section_title": "Ingredients", "reason_for_exclusion": "Yeast and enzymes segment, not ABF Sugar."},
    {"section_title": "Agriculture", "reason_for_exclusion": "AB Agri is not the sugar peer segment."}
  ],
  "scope_warnings": [
    "ABF Group figures must not be treated as ABF Sugar figures unless the source explicitly reports Sugar segment data.",
    "Vivergo is linked to ABF Sugar but reported as disposed and closed operations after closure, so the scope should be clearly labelled."
  ]
}"""
    },
    {
        "step": "2",
        "title": "Strategic evidence chunk generation",
        "subtitle": "Create source-grounded semantic chunks that preserve original evidence and can be used for retrieval and extraction.",
        "pipeline_mapping": "Data Engineering: chunk-document / select-passages",
        "input_hint": "The prompt includes demo source excerpts. For a true chain, replace the demo excerpt with source text selected in Prompt 1.",
        "prompt": f"""You are an information extraction assistant for a competitive intelligence system in the European sugar industry.

Task:
Convert the ABF Sugar source excerpt into strategic evidence chunks.

Definition:
A strategic evidence chunk is not a fixed-length text split. It is a self-contained, source-grounded semantic unit that can later be used for retrieval, evidence display and structured event extraction.

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
1. Use only the DEMO_SOURCE_EXCERPT below.
2. Do not invent facts, values, pages or causes.
3. Do not output placeholder or missing-data error records.
4. Create only meaningful chunks for competitive intelligence.
5. Each chunk must include the original source text supporting category, topic and strategic_signal.
6. Include numeric values only if they are explicitly stated.
7. Separate source-supported facts from strategic interpretation.
8. Return JSON only.

Required output:
Create chunks for at least these topics if supported by the excerpt:
- Sugar revenue and adjusted operating profit deterioration.
- Azucarera restructuring in Spain.
- Vivergo closure and regulatory exposure.
- Ubombo Sugar capacity expansion in Eswatini.
- British Sugar decarbonisation projects.

Output schema:
{{
  "chunks": [
    {{
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
        {{"metric": "...", "value": 0, "unit": "...", "period": "...", "source_text": "..."}}
      ],
      "dashboard_relevance": ["finance", "risk"],
      "confidence": 0.0,
      "limitations": "..."
    }}
  ]
}}

DEMO_SOURCE_EXCERPT:
{DEMO_SOURCE_EXCERPT}""",
        "output": DEMO_CHUNKS_JSON
    },
    {
        "step": "3",
        "title": "Event and indicator record extraction",
        "subtitle": "Convert evidence chunks into dashboard-ready records that can be reviewed and stored.",
        "pipeline_mapping": "Data Engineering: extract-events-json",
        "input_hint": "The prompt includes demo chunks. For a true chain, replace DEMO_INPUT_CHUNKS with the JSON produced by Prompt 2.",
        "prompt": f"""You are converting strategic evidence chunks into dashboard-ready event and indicator records for a Nordzucker competitive intelligence dashboard.

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
9. Return JSON only.

Output schema:
{{
  "event_records": [
    {{
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
    }}
  ],
  "indicator_records": [
    {{
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
    }}
  ]
}}

DEMO_INPUT_CHUNKS:
{DEMO_CHUNKS_JSON}""",
        "output": DEMO_EVENTS_JSON
    },
    {
        "step": "4",
        "title": "Evidence, schema and business logic verification",
        "subtitle": "Check source support and generate the final Human Review payload.",
        "pipeline_mapping": "Data Engineering: link-evidence / schema-precheck / human-review payload preparation",
        "input_hint": "The prompt includes demo chunks and event records. For a true chain, replace them with Prompt 2 and Prompt 3 outputs.",
        "prompt": f"""You are a validation assistant for a competitive intelligence extraction pipeline.

Task:
Verify whether the extracted event and indicator records are supported by the strategic evidence chunks and whether they follow the required schema and taxonomy. Then create the final Human Review payload records.

The Human Review payload is the final presentation output of this prompt chain. It should be understandable as business data: one row per reviewable event, with company, category, event title, summary, source evidence and recommended human action.

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
5. Identify unsupported claims or over-interpretations.
6. Do not create missing-data or placeholder review records.
7. Create final human_review_payload_records only for meaningful, source-supported ABF Sugar events.
8. The final payload must preserve the original source text and clearly separate source-supported facts from business interpretation.
9. Return JSON only.

Output schema:
{{
  "validation_summary": {{"records_checked": 0, "records_supported": 0, "records_requiring_revision": 0, "overall_status": "passed | passed_with_interpretation_notes | failed"}},
  "event_validation": [
    {{"event_id": "...", "schema_status": "passed | failed", "evidence_status": "supported | partially_supported | unsupported", "taxonomy_status": "valid | invalid", "numeric_values_status": "passed | failed | not_applicable", "supported_fields": ["..."], "unsupported_fields": ["..."], "potential_overinterpretations": ["..."], "recommended_human_action": "confirm | edit | reject", "validation_comment": "..."}}
  ],
  "indicator_validation": [
    {{"indicator_id": "...", "schema_status": "passed | failed", "evidence_status": "supported | unsupported", "numeric_value_status": "passed | failed", "recommended_human_action": "confirm | edit | reject", "validation_comment": "..."}}
  ],
  "human_review_payload_records": [
    {{
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
    }}
  ]
}}

DEMO_INPUT_CHUNKS:
{DEMO_CHUNKS_JSON}

DEMO_INPUT_EVENT_AND_INDICATOR_RECORDS:
{DEMO_EVENTS_JSON}""",
        "output": DEMO_FINAL_JSON
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
    ("company", "Company"),
    ("category", "Category"),
    ("event_type", "Event type"),
    ("event_title", "Event title"),
    ("event_summary", "Event summary"),
    ("source_page", "Page"),
    ("source_text", "Evidence"),
    ("validation_status", "Status"),
    ("recommended_human_action", "Action"),
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
                            html.Div(id="pt-final-output-preview"),
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
