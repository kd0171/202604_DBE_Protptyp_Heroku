import pandas as pd
import dash
from dash import html
import dash_bootstrap_components as dbc

from utils import LLM_EVENT_COLUMNS, compact_table, data_note, load_data


dash.register_page(__name__, path="/engineering/structured-events", name="Structured Events")

data = load_data()
events = data["events"].copy()
if "event_id" in events.columns:
    events = events[events["event_id"].astype(str).ne("event_id")]

TABLE_COLUMNS = [
    "event_id", "company_name", "event_type", "country", "city", "site_name",
    "product_category", "target_year", "status", "source_document_title",
    "extraction_confidence", "validation_status", "human_verified", "review_comment",
]


def layout():
    ready = events.copy()
    verified_count = int(ready["human_verified"].astype(str).str.lower().eq("true").sum()) if "human_verified" in ready else 0
    return html.Div(
        [
            html.H2("Data Engineering View: Structured Event Table", className="page-title"),
            html.P(
                "This page shows the structured event table produced by the engineering workflow. It is the handover artifact to the separate Data Analysis View. The analysis pages themselves are not changed.",
                className="page-lead",
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Event records", className="kpi-title"), html.Div(str(len(ready)), className="kpi-value"), html.Div("mock structured output", className="kpi-sub")])), md=3),
                    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Human verified", className="kpi-title"), html.Div(str(verified_count), className="kpi-value"), html.Div("reviewed records", className="kpi-sub")])), md=3),
                    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Downstream use", className="kpi-title"), html.Div("Data Analysis", className="kpi-value-small"), html.Div("separate view remains unchanged", className="kpi-sub")])), md=3),
                    dbc.Col(dbc.Card(dbc.CardBody([html.Div("Persistence", className="kpi-title"), html.Div("conceptual", className="kpi-value-small"), html.Div("backend DB not implemented", className="kpi-sub")])), md=3),
                ],
                className="metric-row",
            ),
            dbc.Card(
                [
                    dbc.CardHeader("Structured events produced by the engineering workflow"),
                    dbc.CardBody(
                        [
                            data_note("llm_extracted_company_events.csv / structured event output", llm_note=True),
                            compact_table(ready, TABLE_COLUMNS, llm_columns=LLM_EVENT_COLUMNS, page_size=10),
                        ]
                    ),
                ],
                className="chart-row",
            ),
            dbc.Card(
                [
                    dbc.CardHeader("Implementation boundary"),
                    dbc.CardBody(
                        html.Ul(
                            [
                                html.Li("Implemented here: frontend table and handover artifact."),
                                html.Li("Not implemented here: production database writes, audit log, authentication, backend API."),
                                html.Li("The Data Analysis View continues to consume the existing mock CSV data without changing its pages."),
                            ]
                        )
                    ),
                ],
                className="chart-row",
            ),
        ]
    )
