import json

import pandas as pd
import dash
from dash import Input, Output, State, callback, dcc, html
import dash_bootstrap_components as dbc

from utils import LLM_EVENT_COLUMNS, compact_table, data_note, load_data


dash.register_page(__name__, path="/engineering/human-review", name="Human Review")

data = load_data()
events = data["events"].copy()
if "event_id" in events.columns:
    events = events[events["event_id"].astype(str).ne("event_id")]

FIELD_COLUMNS = [
    "event_id", "company_name", "event_type", "country", "city", "site_name",
    "product_category", "target_year", "status", "source_text",
    "extraction_confidence", "validation_status", "human_verified", "review_comment",
]

EDIT_FIELDS = [
    "company_name", "event_type", "country", "city", "site_name", "product_category",
    "target_year", "status", "validation_status", "human_verified", "review_comment",
]

EVENT_PROMPT = """You are an information extraction assistant for competitive intelligence.
Extract only explicit events related to investments, plant closures, capacity changes,
decarbonization, partnerships, product expansion and market entries.
For each event, return company_name, event_type, country, city, site_name,
product_category, target_year, status, evidence_text and confidence.
Do not infer facts not supported by the source text."""


def as_records():
    return events.where(pd.notnull(events), "").to_dict("records")


def find_record(records, event_id):
    for record in records:
        if record.get("event_id") == event_id:
            return record
    return records[0] if records else {}


def event_options(records):
    return [
        {
            "label": f"{r.get('event_id')} | {r.get('company_name')} | {r.get('event_type')} | {r.get('validation_status')}",
            "value": r.get("event_id"),
        }
        for r in records
    ]


def status_metrics(records):
    df = pd.DataFrame(records or [])
    total = len(df)
    verified = int(df["human_verified"].astype(str).str.lower().eq("true").sum()) if total and "human_verified" in df else 0
    warnings = int(df["validation_status"].astype(str).str.lower().eq("warning").sum()) if total and "validation_status" in df else 0
    return dbc.Row(
        [
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("Pending review records", className="kpi-title"), html.Div(str(total), className="kpi-value"), html.Div("session-level review queue", className="kpi-sub")])), md=4),
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("Human verified", className="kpi-title"), html.Div(str(verified), className="kpi-value"), html.Div("approved or already checked", className="kpi-sub")])), md=4),
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("Warnings", className="kpi-title"), html.Div(str(warnings), className="kpi-value"), html.Div("requires analyst attention", className="kpi-sub")])), md=4),
        ],
        className="metric-row",
    )


def layout():
    records = as_records()
    first_id = records[0]["event_id"] if records else None
    return html.Div(
        [
            dcc.Store(id="hr-store", data=records),
            html.H2("Data Engineering View: Human Review", className="page-title"),
            html.P(
                "This page deliberately focuses on human-in-the-loop validation. The prompt chain remains in the Upload & Pipeline page; here the analyst checks extracted values against source evidence and approves, edits or rejects records.",
                className="page-lead",
            ),
            html.Div(id="hr-metrics"),
            html.Div(id="hr-global-approval-status"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("1. Select event from review queue"),
                                dbc.CardBody(
                                    [
                                        dbc.Label("Extracted event"),
                                        dcc.Dropdown(id="hr-event-id", options=event_options(records), value=first_id, clearable=False),
                                        html.Div(id="hr-source-preview", className="source-preview-box mt-3"),
                                    ]
                                ),
                            ]
                        ),
                        md=5,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("2. Confirm or correct structured fields"),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col([dbc.Label("company_name"), dbc.Input(id="hr-field-company_name", type="text")], md=6),
                                                dbc.Col([dbc.Label("event_type"), dbc.Input(id="hr-field-event_type", type="text")], md=6),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col([dbc.Label("country"), dbc.Input(id="hr-field-country", type="text")], md=4),
                                                dbc.Col([dbc.Label("city"), dbc.Input(id="hr-field-city", type="text")], md=4),
                                                dbc.Col([dbc.Label("site_name"), dbc.Input(id="hr-field-site_name", type="text")], md=4),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col([dbc.Label("product_category"), dbc.Input(id="hr-field-product_category", type="text")], md=4),
                                                dbc.Col([dbc.Label("target_year"), dbc.Input(id="hr-field-target_year", type="text")], md=4),
                                                dbc.Col([dbc.Label("status"), dbc.Input(id="hr-field-status", type="text")], md=4),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col([dbc.Label("validation_status"), dbc.Input(id="hr-field-validation_status", type="text")], md=6),
                                                dbc.Col([dbc.Label("human_verified"), dcc.Dropdown(id="hr-field-human_verified", options=[{"label": "True", "value": "True"}, {"label": "False", "value": "False"}], clearable=False)], md=6),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Label("review_comment", className="mt-2"),
                                        dbc.Textarea(id="hr-field-review_comment", rows=2),
                                        html.Div(
                                            [
                                                dbc.Button("Save edits", id="hr-save", color="primary", n_clicks=0, className="me-2"),
                                                dbc.Button("Approve", id="hr-approve", color="success", n_clicks=0, className="me-2"),
                                                dbc.Button("Reject", id="hr-reject", color="danger", outline=True, n_clicks=0),
                                            ],
                                            className="mt-3",
                                        ),
                                        html.Div(id="hr-save-status", className="status-text mt-2"),
                                    ]
                                ),
                            ]
                        ),
                        md=7,
                    ),
                ],
                className="chart-row",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Session review table"),
                                dbc.CardBody([data_note("llm_extracted_company_events.csv / session-edited review table", llm_note=True), html.Div(id="hr-table")]),
                            ]
                        ),
                        md=12,
                    )
                ],
                className="chart-row",
            ),
        ]
    )


@callback(Output("hr-metrics", "children"), Input("hr-store", "data"))
def render_metrics(records):
    return status_metrics(records or [])

@callback(Output("hr-global-approval-status", "children"), Input("global-human-validation-store", "data"))
def render_global_approval_status(approval_data):
    if (approval_data or {}).get("approved"):
        return dbc.Alert(
            "Pipeline gate approved. When you return to Upload & Pipeline, Human Review & Validation will be shown as completed.",
            color="success",
            className="mt-2",
        )
    return dbc.Alert(
        "The Upload & Pipeline view is waiting at Human Review & Validation. Check the extracted data and click Approve to release the gate.",
        color="warning",
        className="mt-2",
    )


@callback(
    Output("hr-field-company_name", "value"),
    Output("hr-field-event_type", "value"),
    Output("hr-field-country", "value"),
    Output("hr-field-city", "value"),
    Output("hr-field-site_name", "value"),
    Output("hr-field-product_category", "value"),
    Output("hr-field-target_year", "value"),
    Output("hr-field-status", "value"),
    Output("hr-field-validation_status", "value"),
    Output("hr-field-human_verified", "value"),
    Output("hr-field-review_comment", "value"),
    Output("hr-source-preview", "children"),
    Input("hr-event-id", "value"),
    State("hr-store", "data"),
)
def populate_fields(event_id, records):
    rec = find_record(records or [], event_id)
    source_preview = html.Div(
        [
            html.Div("Evidence text", className="section-label"),
            html.Blockquote(rec.get("source_text", ""), className="source-quote"),
            html.Div(f"Source reference: {rec.get('source_document_title', '')} {rec.get('source_page', '')}", className="source-ref"),
            html.Div("Generated by: extract / event-extraction → evidence-linking", className="generated-by"),
            dbc.Button("View prompt and raw output", id="hr-toggle-prompt", size="sm", color="secondary", outline=True, className="mt-2", n_clicks=0),
            dbc.Collapse(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div("IE prompt", className="section-label"),
                            html.Pre(EVENT_PROMPT, className="prompt-box"),
                            html.Div("Raw extracted record", className="section-label mt-3"),
                            html.Pre(json.dumps({k: rec.get(k, "") for k in FIELD_COLUMNS if k in rec}, indent=2, ensure_ascii=False), className="json-box"),
                        ]
                    )
                ),
                id="hr-prompt-collapse",
                is_open=False,
            ),
        ]
    )
    human_verified = str(rec.get("human_verified", "False"))
    if human_verified not in {"True", "False"}:
        human_verified = "True" if human_verified.lower() == "true" else "False"
    return (
        rec.get("company_name", ""),
        rec.get("event_type", ""),
        rec.get("country", ""),
        rec.get("city", ""),
        rec.get("site_name", ""),
        rec.get("product_category", ""),
        str(rec.get("target_year", "")),
        rec.get("status", ""),
        rec.get("validation_status", ""),
        human_verified,
        rec.get("review_comment", ""),
        source_preview,
    )


@callback(
    Output("hr-prompt-collapse", "is_open"),
    Input("hr-toggle-prompt", "n_clicks"),
    State("hr-prompt-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_prompt(n_clicks, is_open):
    return not is_open


@callback(
    Output("hr-store", "data"),
    Output("hr-save-status", "children"),
    Output("global-human-validation-store", "data"),
    Input("hr-save", "n_clicks"),
    Input("hr-approve", "n_clicks"),
    Input("hr-reject", "n_clicks"),
    State("hr-event-id", "value"),
    State("hr-store", "data"),
    State("hr-field-company_name", "value"),
    State("hr-field-event_type", "value"),
    State("hr-field-country", "value"),
    State("hr-field-city", "value"),
    State("hr-field-site_name", "value"),
    State("hr-field-product_category", "value"),
    State("hr-field-target_year", "value"),
    State("hr-field-status", "value"),
    State("hr-field-validation_status", "value"),
    State("hr-field-human_verified", "value"),
    State("hr-field-review_comment", "value"),
    State("global-human-validation-store", "data"),
    prevent_initial_call=True,
)
def save_review_action(save_clicks, approve_clicks, reject_clicks, event_id, records, company_name, event_type, country, city, site_name, product_category, target_year, status, validation_status, human_verified, review_comment, approval_data):
    trigger = dash.ctx.triggered_id
    records = records or []
    if not event_id:
        return records, "No event selected.", dash.no_update

    next_verified = human_verified or "False"
    next_validation = validation_status or ""
    if trigger == "hr-approve":
        next_verified = "True"
        next_validation = "approved"
    elif trigger == "hr-reject":
        next_verified = "False"
        next_validation = "rejected"

    updated = []
    for rec in records:
        if rec.get("event_id") == event_id:
            rec = {
                **rec,
                "company_name": company_name or "",
                "event_type": event_type or "",
                "country": country or "",
                "city": city or "",
                "site_name": site_name or "",
                "product_category": product_category or "",
                "target_year": target_year or "",
                "status": status or "",
                "validation_status": next_validation,
                "human_verified": next_verified,
                "review_comment": review_comment or "",
            }
        updated.append(rec)

    if trigger == "hr-approve":
        message = f"Approved {event_id}. It is ready for Structured Events and the separate Data Analysis View."
    elif trigger == "hr-reject":
        message = f"Rejected {event_id}. It remains visible for audit and correction."
    else:
        message = f"Saved edits for {event_id}."
    if trigger == "hr-approve":
        approval_payload = {
            "approved": True,
            "approved_event_id": event_id,
            "approved_at": "session",
            "message": "Human validation approved from Human Review page",
        }
    else:
        approval_payload = dash.no_update
    return updated, message, approval_payload


@callback(Output("hr-table", "children"), Input("hr-store", "data"))
def render_review_table(records):
    df = pd.DataFrame(records or [])
    return compact_table(df, FIELD_COLUMNS, llm_columns=LLM_EVENT_COLUMNS, page_size=8, editable=False)
