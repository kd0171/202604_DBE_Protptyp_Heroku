
import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import load_data, compact_table, data_note

dash.register_page(__name__, path="/analysis/market-overview", name="Market Overview")
data = load_data()
market = data["market"]
country_stats = data["country_stats"]

def layout():
    return html.Div([
        html.H2("Data Analysis View: Market Overview", className="page-title"),
        html.P("Public market statistics provide context for competitor events. No LLM-derived values are used on this page.", className="page-lead"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Market indicator"),
                dcc.Dropdown(id="mo-indicator", options=[{"label": x, "value": x} for x in sorted(market["indicator_name"].unique())], value="EU sugar price", clearable=False)
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Year"),
                dcc.Dropdown(id="mo-year", options=[{"label": int(x), "value": int(x)} for x in sorted(country_stats["year"].unique())], value=int(country_stats["year"].max()), clearable=False)
            ])), md=3),
        ], className="control-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Market indicator trend"), dbc.CardBody(dcc.Graph(id="mo-price"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Data table"), dbc.CardBody([data_note("market_indicators.csv"), html.Div(id="mo-price-table")])]), md=5),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Sugar production by country"), dbc.CardBody(dcc.Graph(id="mo-production"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Data table"), dbc.CardBody([data_note("country_sugar_stats.csv"), html.Div(id="mo-production-table")])]), md=5),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Import / export balance by country"), dbc.CardBody(dcc.Graph(id="mo-trade"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Data table"), dbc.CardBody([data_note("country_sugar_stats.csv"), html.Div(id="mo-trade-table")])]), md=5),
        ], className="chart-row"),
    ])

@callback(
    Output("mo-price","figure"), Output("mo-price-table","children"),
    Output("mo-production","figure"), Output("mo-production-table","children"),
    Output("mo-trade","figure"), Output("mo-trade-table","children"),
    Input("mo-indicator","value"), Input("mo-year","value")
)
def update_market(indicator, year):
    m = market[market["indicator_name"] == indicator].copy()
    fig_price = px.line(m, x="year", y="value", markers=True, color="indicator_name")
    fig_price.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10))
    c = country_stats[country_stats["year"] == year].copy().sort_values("sugar_production", ascending=False)
    fig_prod = px.bar(c, x="country", y="sugar_production", hover_data=["beet_production","consumption"])
    fig_prod.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Sugar production, kt")
    c_trade = c.sort_values("net_export", ascending=False)
    fig_trade = px.bar(c_trade, x="country", y="net_export", hover_data=["import_volume","export_volume","consumption"])
    fig_trade.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Net export, kt")
    return (
        fig_price, compact_table(m, ["year","month","indicator_name","region","value","unit","source_name"], page_size=6),
        fig_prod, compact_table(c, ["country","iso_alpha","year","sugar_production","beet_production","consumption"], page_size=7),
        fig_trade, compact_table(c_trade, ["country","iso_alpha","year","import_volume","export_volume","net_export","consumption"], page_size=7)
    )
