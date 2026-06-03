
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import load_data, compact_table, data_note, LLM_EVENT_COLUMNS, match_query, apply_interactive_filters

dash.register_page(__name__, path="/analysis/interactive-mode", name="Interactive Mode")
data = load_data()
events = data["events"]
queries = data["interactive_queries"]

def layout():
    return html.Div([
        html.H2("Interactive Mode: RAG-like Natural Language Exploration", className="page-title"),
        html.P("This page simulates a natural-language interaction layer. It maps questions to analytical intents, retrieves structured event records, and displays a source-grounded summary with related charts and evidence.", className="page-lead"),
        dbc.Alert("This view provides a natural-language style entry point to the structured event data. The answer is linked to filtered records, charts and source evidence.", color="info"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Ask a question"),
                dbc.CardBody([
                    dbc.Label("Natural-language style question"),
                    dcc.Input(id="ia-question", value="Which competitor investment and operational improvement events were extracted for Europe since 2023?", className="question-input"),
                    dbc.Button("Ask", id="ia-ask", color="primary", className="mt-2"),
                    html.Div("Suggested examples:", className="section-label mt-3"),
                    html.Ul([html.Li(q["example_questions"][0]) for q in queries])
                ])
            ]), md=5),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Generated answer summary"),
                dbc.CardBody(html.Div(id="ia-answer"))
            ]), md=7)
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Related event count by country"), dbc.CardBody(dcc.Graph(id="ia-count"))]), md=6),
            dbc.Col(dbc.Card([dbc.CardHeader("Related event map"), dbc.CardBody(dcc.Graph(id="ia-map"))]), md=6),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Evidence table"), dbc.CardBody([data_note("llm_extracted_company_events.csv filtered by intent", llm_note=True), html.Div(id="ia-table")])]), md=12),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Validation explanation"),
                dbc.CardBody(html.Div(id="ia-validation"))
            ]), md=12)
        ], className="chart-row")
    ])

@callback(
    Output("ia-answer","children"),
    Output("ia-count","figure"),
    Output("ia-map","figure"),
    Output("ia-table","children"),
    Output("ia-validation","children"),
    Input("ia-ask","n_clicks"),
    State("ia-question","value")
)
def update_interactive(n_clicks, question):
    intent = match_query(question, queries)
    df = apply_interactive_filters(events, intent.get("filters", {}))
    count_country = df.groupby("country").size().reset_index(name="event_count")
    fig_count = px.bar(count_country, x="country", y="event_count") if not count_country.empty else px.bar()
    fig_count.update_layout(height=330, margin=dict(l=10,r=10,t=10,b=10))
    df_map = df.dropna(subset=["latitude","longitude"]).copy()
    fig_map = px.scatter_geo(
        df_map, lat="latitude", lon="longitude", color="event_type",
        hover_name="source_text", hover_data=["company_name","country","city","source_text"],
        scope="europe"
    ) if not df_map.empty else px.scatter_geo()
    fig_map.update_layout(height=330, margin=dict(l=10,r=10,t=10,b=10))

    top_country = count_country.sort_values("event_count", ascending=False).iloc[0].to_dict() if not count_country.empty else {"country":"No data","event_count":0}
    answer = html.Div([
        html.H4(intent["answer_title"]),
        html.P(intent["answer_summary"]),
        html.Div([
            html.Span("SQL-grounded values: ", className="data-note-label"),
            html.Span(f"{len(df)} matching event records; top country = {top_country['country']} ({top_country['event_count']} events).")
        ], className="answer-fact-box"),
        html.Div([
            html.Span("Charts selected by intent: ", className="data-note-label"),
            html.Span(", ".join(intent.get("charts", [])))
        ], className="answer-fact-box"),
    ])

    table_cols = ["event_id","company_name","event_type","country","city","site_name","product_category","status","source_text","human_verified"]
    validation = html.Div([
        html.P(intent.get("validation_note","")),
        html.Ul([
            html.Li("Counts are computed from the filtered event table, not invented by the summary text."),
            html.Li("Qualitative claims are linked to event_id and source_text."),
            html.Li("Counts and company lists are derived from the filtered event records displayed on this page."),
        ])
    ])
    return answer, fig_count, fig_map, compact_table(df, table_cols, llm_columns=LLM_EVENT_COLUMNS, page_size=7), validation
