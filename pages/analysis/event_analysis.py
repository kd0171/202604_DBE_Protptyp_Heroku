
import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import load_data, compact_table, data_note, LLM_EVENT_COLUMNS

dash.register_page(__name__, path="/analysis/event-analysis", name="Event Analysis")
data = load_data()
events = data["events"]

def layout():
    return html.Div([
        html.H2("Competitor Event Analysis", className="page-title"),
        html.P("This page visualizes records created by the  LLM document-to-table pipeline. Yellow cells are LLM-extracted fields.", className="page-lead"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Company"),
                dcc.Dropdown(id="ev-company", options=[{"label":"All","value":"all"}]+[{"label": x, "value": x} for x in sorted(events["company_name"].unique())], value="all", clearable=False),
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Event type"),
                dcc.Dropdown(id="ev-type", options=[{"label":"All","value":"all"}]+[{"label": x, "value": x} for x in sorted(events["event_type"].unique())], value="all", clearable=False),
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Country"),
                dcc.Dropdown(id="ev-country", options=[{"label":"All","value":"all"}]+[{"label": x, "value": x} for x in sorted(events["country"].unique())], value="all", clearable=False),
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Verification"),
                dcc.Checklist(id="ev-verified", options=[{"label":"Human verified only","value":"verified"}], value=[], inline=True),
            ])), md=3),
        ], className="control-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Investment / event map"), dbc.CardBody(dcc.Graph(id="ev-map"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Data table"), dbc.CardBody([data_note("llm_extracted_company_events.csv", llm_note=True), html.Div(id="ev-map-table")])]), md=5),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Event count by country and event type"), dbc.CardBody(dcc.Graph(id="ev-count"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Aggregated data table"), dbc.CardBody([data_note("llm_extracted_company_events.csv aggregated", llm_note=True), html.Div(id="ev-count-table")])]), md=5),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Event timeline"), dbc.CardBody(dcc.Graph(id="ev-timeline"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Event detail table"), dbc.CardBody([data_note("llm_extracted_company_events.csv", llm_note=True), html.Div(id="ev-detail-table")])]), md=5),
        ], className="chart-row"),
    ])

def filter_events(company, ev_type, country, verified):
    df = events.copy()
    if company != "all":
        df = df[df["company_name"] == company]
    if ev_type != "all":
        df = df[df["event_type"] == ev_type]
    if country != "all":
        df = df[df["country"] == country]
    if "verified" in verified:
        df = df[df["human_verified"] == True]
    return df

@callback(
    Output("ev-map","figure"), Output("ev-map-table","children"),
    Output("ev-count","figure"), Output("ev-count-table","children"),
    Output("ev-timeline","figure"), Output("ev-detail-table","children"),
    Input("ev-company","value"), Input("ev-type","value"), Input("ev-country","value"), Input("ev-verified","value"),
)
def update_events(company, ev_type, country, verified):
    df = filter_events(company, ev_type, country, verified)
    df_map = df.dropna(subset=["latitude","longitude"]).copy()
    fig_map = px.scatter_geo(
        df_map, lat="latitude", lon="longitude", color="event_type",
        symbol="company_name", hover_name="source_text",
        hover_data=["company_name","country","city","site_name","product_category","status","source_text"],
        scope="europe"
    ) if not df_map.empty else px.scatter_geo()
    fig_map.update_layout(height=430, margin=dict(l=10,r=10,t=10,b=10))
    agg = df.groupby(["country","event_type"]).size().reset_index(name="event_count")
    fig_count = px.bar(agg, x="country", y="event_count", color="event_type", barmode="stack") if not agg.empty else px.bar()
    fig_count.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10))
    df_t = df.copy()
    df_t["plot_year"] = df_t["target_year"].fillna(df_t["start_year"]).fillna(df_t["source_year"])
    fig_time = px.scatter(
        df_t, x="plot_year", y="company_name", color="event_type",
        hover_name="source_text", hover_data=["country","city","status","source_text"]
    ) if not df_t.empty else px.scatter()
    fig_time.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="Target / start / source year")
    table_cols = ["event_id","company_name","event_type","country","city","site_name","product_category","production_type","status","source_text","extraction_confidence","human_verified"]
    return (
        fig_map, compact_table(df, table_cols, llm_columns=LLM_EVENT_COLUMNS, page_size=6),
        fig_count, compact_table(agg, ["country","event_type","event_count"], llm_columns={"country","event_type"}, page_size=8),
        fig_time, compact_table(df, table_cols, llm_columns=LLM_EVENT_COLUMNS, page_size=6),
    )
