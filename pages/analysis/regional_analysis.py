
import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import load_data, compact_table, data_note, capacity_size

dash.register_page(__name__, path="/analysis/regional-analysis", name="Regional Analysis")
data = load_data()
country_stats = data["country_stats"]
sites = data["sites"]

def layout():
    metrics = ["sugar_production","beet_production","import_volume","export_volume","net_export","consumption"]
    return html.Div([
        html.H2("Regional Market & Site Analysis", className="page-title"),
        html.P("This page combines country-level public market data with curated company site data.", className="page-lead"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Map metric"),
                dcc.Dropdown(id="ra-metric", options=[{"label": m, "value": m} for m in metrics], value="sugar_production", clearable=False),
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Site type"),
                dcc.Dropdown(id="ra-site-type", options=[{"label":"All","value":"all"}]+[{"label": x, "value": x} for x in sorted(sites["site_type"].unique())], value="all", clearable=False),
            ])), md=3),
        ], className="control-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Country market map"), dbc.CardBody(dcc.Graph(id="ra-country-map"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Data table"), dbc.CardBody([data_note("country_sugar_stats.csv"), html.Div(id="ra-country-table")])]), md=5),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Company site map, city level"), dbc.CardBody(dcc.Graph(id="ra-site-map"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Data table"), dbc.CardBody([data_note("company_sites.csv"), html.Div(id="ra-site-table")])]), md=5),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Site count by country and company"), dbc.CardBody(dcc.Graph(id="ra-site-count"))]), md=7),
            dbc.Col(dbc.Card([dbc.CardHeader("Aggregated data table"), dbc.CardBody([data_note("company_sites.csv aggregated"), html.Div(id="ra-site-count-table")])]), md=5),
        ], className="chart-row"),
    ])

@callback(
    Output("ra-country-map","figure"), Output("ra-country-table","children"),
    Output("ra-site-map","figure"), Output("ra-site-table","children"),
    Output("ra-site-count","figure"), Output("ra-site-count-table","children"),
    Input("ra-metric","value"), Input("ra-site-type","value"),
)
def update_regional(metric, site_type):
    c = country_stats.copy()
    fig_map = px.choropleth(
        c, locations="iso_alpha", color=metric, hover_name="country",
        hover_data=["sugar_production","beet_production","import_volume","export_volume","net_export","consumption"],
        scope="europe", color_continuous_scale="Blues"
    )
    fig_map.update_layout(height=430, margin=dict(l=10,r=10,t=10,b=10))
    s = sites.copy()
    if site_type != "all":
        s = s[s["site_type"] == site_type]
    s["marker_size"] = capacity_size(s["capacity_class"])
    fig_sites = px.scatter_geo(
        s, lat="latitude", lon="longitude", color="company_name", size="marker_size",
        hover_name="site_name", hover_data=["city","country","site_type","products","capacity_class","human_verified"],
        scope="europe"
    )
    fig_sites.update_layout(height=430, margin=dict(l=10,r=10,t=10,b=10))
    agg = s.groupby(["country","company_name"]).size().reset_index(name="site_count")
    fig_count = px.bar(agg, x="country", y="site_count", color="company_name", barmode="stack")
    fig_count.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10))
    return (
        fig_map, compact_table(c[["country","iso_alpha","year",metric,"sugar_production","beet_production","net_export"]], page_size=8),
        fig_sites, compact_table(s, ["site_id","company_name","site_name","city","country","latitude","longitude","site_type","products","capacity_class","human_verified"], page_size=7),
        fig_count, compact_table(agg, ["country","company_name","site_count"], page_size=8),
    )
