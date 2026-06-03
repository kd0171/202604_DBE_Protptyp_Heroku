
import dash
from dash import html
import dash_bootstrap_components as dbc
from utils import load_data, compact_table

dash.register_page(__name__, path="/engineering/pipeline-overview", name="Pipeline Overview")
data = load_data()
steps = data["pipeline_steps"]

def layout():
    cards = []
    for row in steps.itertuples():
        cards.append(dbc.Col(dbc.Card(dbc.CardBody([
            html.Div(f"Step {row.step_no}", className="step-label"),
            html.Div(row.step_name, className="step-title"),
            html.P(row.description, className="step-text"),
            html.Div(row.artifact, className="artifact-pill"),
        ]), className="step-card"), md=4))
    return html.Div([
        html.H2("Data Engineering View: Pipeline Overview", className="page-title"),
        html.P("This is the main function of the data product: selected public documents are converted into structured competitor event data. The LLM is used for factual extraction, not for risk judgement.", className="page-lead"),
        dbc.Row(cards, className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Pipeline step table"),
                dbc.CardBody(compact_table(steps, page_size=6))
            ]), md=12)
        ], className="chart-row")
    ])
