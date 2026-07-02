import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


dash.register_page(__name__, path="/analysis/interactive-mode", name="Interactive Mode")


def layout():
    return html.Div([
        html.H2("Interactive Mode moved into the Analysis Workspace", className="page-title"),
        html.P(
            "The interactive question-and-answer mode is now part of the main Data Analysis View. "
            "Use the Dashboard / Interactive Mode switch in the upper-left corner of the Analysis Workspace.",
            className="page-lead",
        ),
        dbc.Button("Open Analysis Workspace", href="/analysis/competitive-scorecard", color="primary"),
    ])
