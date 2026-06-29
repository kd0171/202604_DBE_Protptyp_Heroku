
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Home")

def layout():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div("Business Informatics PoC", className="home-kicker"),
                html.H1("Nordzucker Competitor Intelligence Data Product", className="home-title"),
                html.P(
                    "A two-view PoC that demonstrates how curated public documents can be converted into structured competitor event data and then explored through dashboards and a RAG-like interactive interface.",
                    className="home-lead"
                ),
                dbc.Alert(
                    "This PoC demonstrates PDF upload, prompt-chain execution, RAG storage placeholder, event extraction, review, storage and analysis in one workflow.",
                    color="info",
                    className="home-alert"
                ),
            ], md=12)
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Main function", className="home-card-label"),
                html.H3("Data Engineering View", className="home-card-title"),
                html.P(
                    "PDF upload and GitLab CI/CD-style prompt-chain pipeline for preparing RAG-ready documents and structured event records.",
                    className="home-card-text"
                ),
                dbc.Button("Open Data Engineering View", href="/engineering/upload-pipeline", color="primary"),
            ]), className="home-card"), md=6),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Value demonstration", className="home-card-label"),
                html.H3("Data Analysis View", className="home-card-title"),
                html.P(
                    "Dashboards and interactive exploration for market context, regional competitor activity, extracted events, and source-grounded summaries.",
                    className="home-card-text"
                ),
                dbc.Button("Open Data Analysis View", href="/analysis/market-overview", color="secondary"),
            ]), className="home-card"), md=6),
        ], className="chart-row")
    ])
