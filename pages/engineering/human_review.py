
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
from utils import load_data, compact_table, data_note, LLM_EVENT_COLUMNS

dash.register_page(__name__, path="/engineering/human-review", name="Human Review")
data = load_data()
events = data["events"]

EDIT_FIELDS = [
    "event_type",
    "country",
    "city",
    "site_name",
    "product_category",
    "target_year",
    "status",
    "validation_status",
    "human_verified",
    "review_comment",
]

TABLE_COLUMNS = [
    "event_id", "company_name", "event_type", "country", "city", "site_name",
    "product_category", "target_year", "status", "source_text", 
    "validation_status", "human_verified", "review_comment"
]

def as_records():
    return events.where(pd.notnull(events), "").to_dict("records")

def find_record(records, event_id):
    for r in records:
        if r.get("event_id") == event_id:
            return r
    return records[0] if records else {}

def layout():
    initial_records = as_records()
    first_id = initial_records[0]["event_id"] if initial_records else None
    return html.Div([
        dcc.Store(id="hr-store", data=initial_records),
        html.H2("Human Review & Validation", className="page-title"),
        html.P(
            "This page supports human-in-the-loop review. The analyst selects one event, edits explicit text fields, and saves the update.",
            className="page-lead"
        ),
        dbc.Alert(
            "Changes are reflected in the reviewed event table below.",
            color="info"
        ),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("1. Select extracted event"),
                dbc.CardBody([
                    dbc.Label("Event record"),
                    dcc.Dropdown(
                        id="hr-event-id",
                        options=[
                            {
                                "label": f"{r['event_id']} | {r['company_name']} | {r['event_type']} | {r['country']}",
                                "value": r["event_id"]
                            }
                            for r in initial_records
                        ],
                        value=first_id,
                        clearable=False
                    ),
                    html.Div(id="hr-source-preview", className="source-preview-box mt-3")
                ])
            ]), md=5),

            dbc.Col(dbc.Card([
                dbc.CardHeader("2. Edit selected fields"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([dbc.Label("event_type"), dbc.Input(id="hr-field-event_type", type="text")], md=6),
                        dbc.Col([dbc.Label("country"), dbc.Input(id="hr-field-country", type="text")], md=6),
                    ]),
                    dbc.Row([
                        dbc.Col([dbc.Label("city"), dbc.Input(id="hr-field-city", type="text")], md=6),
                        dbc.Col([dbc.Label("site_name"), dbc.Input(id="hr-field-site_name", type="text")], md=6),
                    ], className="mt-2"),
                    dbc.Row([
                        dbc.Col([dbc.Label("product_category"), dbc.Input(id="hr-field-product_category", type="text")], md=6),
                        dbc.Col([dbc.Label("target_year"), dbc.Input(id="hr-field-target_year", type="text")], md=6),
                    ], className="mt-2"),
                    dbc.Row([
                        dbc.Col([dbc.Label("status"), dbc.Input(id="hr-field-status", type="text")], md=6),
                        dbc.Col([dbc.Label("validation_status"), dbc.Input(id="hr-field-validation_status", type="text")], md=6),
                    ], className="mt-2"),
                    dbc.Row([
                        dbc.Col([dbc.Label("human_verified"), dbc.Input(id="hr-field-human_verified", type="text")], md=6),
                        dbc.Col([dbc.Label("review_comment"), dbc.Input(id="hr-field-review_comment", type="text")], md=6),
                    ], className="mt-2"),
                    dbc.Button("Save selected event update", id="hr-save", color="primary", n_clicks=0, className="mt-3"),
                    html.Div(id="hr-save-status", className="status-text mt-2")
                ])
            ]), md=7),
        ], className="chart-row"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Reviewed event table, updated from session store"),
                dbc.CardBody([
                    data_note("llm_extracted_company_events.csv / session-edited review table", llm_note=True),
                    html.Div(id="hr-table")
                ])
            ]), md=12)
        ], className="chart-row"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Data flow for reliable updates"),
                dbc.CardBody([
                    html.Ol([
                        html.Li("The selected event_id is used as the stable primary key."),
                        html.Li("Input fields are populated from dcc.Store."),
                        html.Li("Save updates only the matching event_id record inside dcc.Store."),
                        html.Li("The reviewed event table is updated immediately after saving."),
                        html.Li("The same event_id-based update structure is used for database storage.")
                    ])
                ])
            ]), md=12)
        ], className="chart-row")
    ])

@callback(
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
    State("hr-store", "data")
)
def populate_fields(event_id, records):
    rec = find_record(records or [], event_id)
    source_preview = html.Div([
        html.Div("Source text used as evidence", className="section-label"),
        html.Blockquote(rec.get("source_text", ""), className="source-quote"),
        html.Div("Structured fields below are the extracted values from this source text.", className="section-label")
    ])
    return (
        rec.get("event_type", ""),
        rec.get("country", ""),
        rec.get("city", ""),
        rec.get("site_name", ""),
        rec.get("product_category", ""),
        rec.get("target_year", ""),
        rec.get("status", ""),
        rec.get("validation_status", ""),
        str(rec.get("human_verified", "")),
        rec.get("review_comment", ""),
        source_preview
    )

@callback(
    Output("hr-store", "data"),
    Output("hr-save-status", "children"),
    Input("hr-save", "n_clicks"),
    State("hr-event-id", "value"),
    State("hr-store", "data"),
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
    prevent_initial_call=True
)
def save_selected_event(n_clicks, event_id, records, event_type, country, city, site_name,
                        product_category, target_year, status, validation_status,
                        human_verified, review_comment):
    if not records or not event_id:
        return records, "No record selected."

    updated = []
    saved = False
    new_values = {
        "event_type": event_type or "",
        "country": country or "",
        "city": city or "",
        "site_name": site_name or "",
        "product_category": product_category or "",
        "target_year": target_year or "",
        "status": status or "",
        "validation_status": validation_status or "",
        "human_verified": human_verified or "",
        "review_comment": review_comment or "",
    }

    for rec in records:
        if rec.get("event_id") == event_id:
            rec = {**rec, **new_values}
            saved = True
        updated.append(rec)

    if saved:
        return updated, f"Saved updates for {event_id} in session."
    return records, f"Could not find event_id {event_id}."

@callback(
    Output("hr-table", "children"),
    Input("hr-store", "data")
)
def render_table(records):
    df = pd.DataFrame(records or [])
    return compact_table(
        df,
        TABLE_COLUMNS,
        llm_columns=LLM_EVENT_COLUMNS,
        page_size=8,
        editable=False
    )
