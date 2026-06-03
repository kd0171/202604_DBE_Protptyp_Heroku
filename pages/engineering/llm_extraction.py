
import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import json
from utils import load_data, compact_table, data_note, LLM_EVENT_COLUMNS

dash.register_page(__name__, path="/engineering/llm-extraction", name="LLM Extraction")
data = load_data()
sources = data["sources"]
events = data["events"]

PROMPT = """Extract factual company events from the selected official document.

Do not judge risk.
Do not evaluate whether the event is good or bad for Nordzucker.
Do not infer unsupported values.

Extract only explicitly mentioned events:
- investment
- capacity expansion or reduction
- plant closure
- plant modernization
- energy efficiency measure
- decarbonization investment
- bioethanol, starch, logistics or packaging activities

Return JSON with:
company_name, event_type, event_presence, country, city, site_name,
business_segment, product_category, production_type, target_year,
status, source_text.
"""

def layout():
    return html.Div([
        html.H2(" LLM Extraction", className="page-title"),
        html.P("This page applies the extraction prompt to the registered document and displays extracted source snippets, JSON and structured event rows after running the extraction.", className="page-lead"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Input document and prompt"),
                dbc.CardBody([
                    dbc.Label("Source document"),
                    dcc.Dropdown(
                        id="le-source",
                        options=[{"label": f"{r.company_name} — {r.document_title}", "value": r.source_id} for r in sources.itertuples()],
                        value="SRC_PL_ESG_2023",
                        clearable=False
                    ),
                    html.Hr(),
                    html.Div("Prompt template", className="section-label"),
                    html.Pre(PROMPT, className="prompt-box"),
                    dbc.Button("Run LLM extraction", id="le-run", color="primary", n_clicks=0),
                    html.Div(id="le-status", className="status-text mt-2")
                ])
            ]), md=5),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Source text preview"),
                dbc.CardBody(html.Div(id="le-source-preview"))
            ]), md=7),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Extracted JSON preview"),
                dbc.CardBody(html.Div(id="le-json-container"))
            ]), md=5),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Extracted event table"),
                dbc.CardBody(html.Div(id="le-table-container"))
            ]), md=7),
        ], className="chart-row")
    ])

@callback(
    Output("le-status", "children"),
    Output("le-source-preview", "children"),
    Output("le-json-container", "children"),
    Output("le-table-container", "children"),
    Input("le-source", "value"),
    Input("le-run", "n_clicks"),
)
def update_extraction(source_id, n_clicks):
    if not n_clicks:
        placeholder = dbc.Alert("Click Run LLM extraction to display extracted source snippets, JSON and structured event rows.", color="light")
        return "No extraction has been run yet.", placeholder, placeholder, placeholder

    subset = events[events["source_id"] == source_id].copy()
    if subset.empty:
        subset = events.head(1).copy()

    text_items = [html.Div([
        html.Div(f"Evidence snippet {i+1}", className="section-label"),
        html.Blockquote(row.source_text, className="source-quote")
    ]) for i, row in enumerate(subset.itertuples())]

    json_cols = [
        "company_name","event_type","event_presence","country","city","site_name",
        "business_segment","product_category","production_type","target_year","status","source_text"
    ]
    records = subset[[c for c in json_cols if c in subset.columns]].replace({float("nan"): None}).to_dict("records")

    table_cols = ["event_id","company_name","event_type","country","city","site_name","product_category","status","source_text","extraction_confidence"]
    return (
        f"Extraction completed for {len(subset)} event record(s).",
        text_items,
        html.Pre(json.dumps(records, indent=2, ensure_ascii=False, default=str), className="json-box"),
        html.Div([data_note("llm_extracted_company_events.csv", llm_note=True), compact_table(subset, table_cols, llm_columns=LLM_EVENT_COLUMNS, page_size=5)])
    )
