
import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import load_data, compact_table, data_note, country_score

dash.register_page(__name__, path="/analysis/combined-interpretation", name="Combined Interpretation")
data = load_data()
country_stats = data["country_stats"]
sites = data["sites"]
events = data["events"]

def layout():
    return html.Div([
        html.H2("Combined Regional Interpretation", className="page-title"),
        html.P("Public statistics, site footprint and LLM-extracted event counts are combined. The score is rule-based, not an LLM risk judgement.", className="page-lead"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Map value"),
                dcc.Dropdown(
                    id="ci-metric",
                    options=[
                        {"label":"Regional activity score", "value":"regional_activity_score"},
                        {"label":"Sugar production", "value":"sugar_production"},
                        {"label":"Site count", "value":"site_count"},
                        {"label":"Event count", "value":"event_count"},
                        {"label":"Net export", "value":"net_export"},
                    ],
                    value="regional_activity_score",
                    clearable=False
                )
            ])), md=4),
        ], className="control-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Regional activity map"), dbc.CardBody(dcc.Graph(id="ci-map"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Data table"), dbc.CardBody([data_note("country_sugar_stats.csv + company_sites.csv + llm_extracted_company_events.csv", llm_note=True), html.Div(id="ci-map-table")])]), md=5),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Country summary matrix"), dbc.CardBody(dcc.Graph(id="ci-matrix"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Summary table"), dbc.CardBody([data_note("combined aggregation; event_count comes from LLM events", llm_note=True), html.Div(id="ci-summary-table")])]), md=5),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Country explanation cards"), dbc.CardBody(html.Div(id="ci-cards"))]), md=12),
        ], className="chart-row"),
    ])

@callback(
    Output("ci-map","figure"), Output("ci-map-table","children"),
    Output("ci-matrix","figure"), Output("ci-summary-table","children"),
    Output("ci-cards","children"),
    Input("ci-metric","value"),
)
def update_combined(metric):
    df = country_score(country_stats, sites, events)
    fig_map = px.choropleth(
        df, locations="iso_alpha", color=metric, hover_name="country",
        hover_data=["sugar_production","net_export","site_count","company_count","event_count","regional_activity_score"],
        scope="europe", color_continuous_scale="Blues"
    )
    fig_map.update_layout(height=430, margin=dict(l=10,r=10,t=10,b=10))
    cols = ["country","sugar_production","net_export","site_count","company_count","event_count","regional_activity_score"]
    long = df[cols].melt(id_vars="country", var_name="metric", value_name="value")
    fig_matrix = px.density_heatmap(long, x="metric", y="country", z="value", histfunc="sum", text_auto=True)
    fig_matrix.update_layout(height=430, margin=dict(l=10,r=10,t=10,b=10))
    top = df.sort_values("regional_activity_score", ascending=False).head(4)
    cards = []
    for r in top.itertuples():
        cards.append(dbc.Col(dbc.Card(dbc.CardBody([
            html.Div(r.country, className="insight-title"),
            html.Div(f"Regional activity score: {r.regional_activity_score}", className="insight-meta"),
            html.P(f"Production: {r.sugar_production} kt | Net export: {r.net_export} kt", className="insight-text"),
            html.P(f"Sites: {int(r.site_count)} | Companies: {int(r.company_count)} | LLM-extracted events: {int(r.event_count)}", className="insight-text"),
            html.Div("Rule-based interpretation. No LLM risk score is used.", className="insight-badge"),
        ]), className="insight-card"), md=3))
    return (
        fig_map, compact_table(df[cols], llm_columns={"event_count"}, page_size=8),
        fig_matrix, compact_table(df[cols], llm_columns={"event_count"}, page_size=8),
        dbc.Row(cards)
    )
