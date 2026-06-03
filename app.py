
from dash import Dash, html, dcc, Input, Output
import dash
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = "Nordzucker Competitor Intelligence Data Product"

engineering_links = [
    ("Pipeline Overview", "/engineering/pipeline-overview"),
    ("Source Registration", "/engineering/upload-register"),
    ("LLM Extraction", "/engineering/llm-extraction"),
    ("Human Review", "/engineering/human-review"),
    ("Save to Database", "/engineering/save-database"),
]

analysis_links = [
    ("Market Overview", "/analysis/market-overview"),
    ("Regional Analysis", "/analysis/regional-analysis"),
    ("Event Analysis", "/analysis/event-analysis"),
    ("Combined Interpretation", "/analysis/combined-interpretation"),
    ("Interactive Mode", "/analysis/interactive-mode"),
]

def make_links(items, pathname):
    return [
        dbc.NavLink(
            label,
            href=href,
            active=(pathname == href),
            className="sub-nav-link"
        )
        for label, href in items
    ]

app.layout = html.Div([
    dcc.Location(id="url"),
    dbc.Navbar(
        dbc.Container([
            html.A([
                html.Div("Nordzucker Competitor Intelligence Data Product", className="app-title"),
                html.Div("LLM document-to-table pipeline + data analysis + RAG-like interaction", className="app-subtitle"),
            ], href="/", className="brand-link"),
            dbc.Nav([
                dbc.NavLink("Home", href="/", id="top-home"),
                dbc.NavLink("Data Engineering View", href="/engineering/pipeline-overview", id="top-engineering"),
                dbc.NavLink("Data Analysis View", href="/analysis/market-overview", id="top-analysis"),
            ], pills=True, className="top-view-tabs")
        ], fluid=True),
        color="white",
        className="top-navbar",
    ),
    dbc.Container([
        html.Div(id="sub-navigation", className="sub-navigation"),
        dash.page_container
    ], fluid=True, className="page-container")
])

@app.callback(
    Output("sub-navigation", "children"),
    Output("sub-navigation", "style"),
    Output("top-home", "active"),
    Output("top-engineering", "active"),
    Output("top-analysis", "active"),
    Input("url", "pathname")
)
def update_subnav(pathname):
    pathname = pathname or "/"
    if pathname == "/":
        return "", {"display": "none"}, True, False, False
    if pathname.startswith("/analysis"):
        return dbc.Nav(make_links(analysis_links, pathname), pills=True), {}, False, False, True
    if pathname.startswith("/engineering"):
        return dbc.Nav(make_links(engineering_links, pathname), pills=True), {}, False, True, False
    return "", {"display": "none"}, False, False, False

if __name__ == "__main__":
    app.run(debug=True)
