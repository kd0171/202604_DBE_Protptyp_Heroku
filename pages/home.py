from __future__ import annotations

from pathlib import Path

import dash
from dash import Input, Output, State, callback, ctx, dcc, html
import dash_bootstrap_components as dbc


dash.register_page(__name__, path="/", name="Home")

APP_ROOT = Path(__file__).resolve().parents[1]

HOME_TUTORIAL_STEPS = [
    {
        "title": "1. Welcome",
        "text": """
#### Welcome to the prototype

This application demonstrates a simplified competitive-intelligence data product for the sugar industry.

The prototype has three main entry points:

1. **Data Engineering View** — demonstrates the PDF-to-structured-data workflow, including prompt-configured extraction, evidence linking, Human Review and database publication.
2. **Prompt Test** — shows a simplified manual prompt chain that can be tested with an external LLM interface.
3. **Data Analysis View** — shows how structured competitor and market data can be explored in dashboards.

Click **Next** to see the navigation flow.
""",
        "hint": "This tutorial is intentionally short. The detailed workflows are explained inside the Data Engineering View and Prompt Test pages.",
    },
    {
        "title": "2. Navigate between the main views",
        "media_src": "/assets/tutorial/home/HomePage.gif",
        "media_alt": "Tutorial GIF showing navigation from the Home page to Data Engineering View, Prompt Test and Data Analysis View.",
        "text": """
#### Main navigation

Use the buttons on the Home page to open the three prototype areas in this order:

1. **Data Engineering View**
2. **Prompt Test**
3. **Data Analysis View**

This GIF is sufficient for the Home page because the Home page only explains how to enter the main workflows.
""",
        "hint": "The GIF file should be stored at assets/tutorial/home/HomePage.gif.",
    },
]


def _asset_file_exists(asset_src: str) -> bool:
    if not asset_src.startswith("/assets/"):
        return False
    rel = asset_src.replace("/assets/", "assets/", 1)
    return (APP_ROOT / rel).exists()


def _tutorial_media(item):
    media_src = item.get("media_src")
    if not media_src:
        return None, {"display": "none"}
    if _asset_file_exists(media_src):
        return html.Img(
            src=media_src,
            alt=item.get("media_alt", "Tutorial media"),
            className="tutorial-media-image",
        ), {}
    return html.Div(
        [
            html.Div("Tutorial GIF placeholder", className="tutorial-media-label"),
            html.Div(f"Place the GIF file at: {media_src}", className="tutorial-media-subtitle"),
        ],
        className="tutorial-missing-media-box",
    ), {}


def home_tutorial_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(id="home-tutorial-title")),
            dbc.ModalBody(
                [
                    html.Div(id="home-tutorial-progress", className="tutorial-progress-text"),
                    html.Div(id="home-tutorial-media", className="tutorial-media-placeholder"),
                    html.Div(id="home-tutorial-text", className="tutorial-main-text"),
                    html.Div(id="home-tutorial-hint", className="tutorial-hint-box"),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Skip tutorial", id="home-tutorial-skip", color="secondary", outline=True, className="me-auto", n_clicks=0),
                    dbc.Button("Previous", id="home-tutorial-prev", color="secondary", outline=True, n_clicks=0),
                    dbc.Button("Next", id="home-tutorial-next", color="primary", n_clicks=0),
                ]
            ),
        ],
        id="home-tutorial-modal",
        centered=True,
        size="xl",
        backdrop="static",
        keyboard=False,
        is_open=True,
    )


def layout():
    return html.Div([
        dcc.Store(id="home-tutorial-store", storage_type="session", data={"open": True, "step": 0, "completed": False}),
        home_tutorial_modal(),
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
            ], md=9),
            dbc.Col(
                dbc.Button("Tutorial", id="home-open-tutorial", color="info", outline=True, size="sm", n_clicks=0),
                md=3,
                className="text-md-end mt-2 mt-md-0",
            ),
        ], className="align-items-start"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Main function", className="home-card-label"),
                html.H3("Data Engineering View", className="home-card-title"),
                html.P(
                    "PDF upload and GitLab CI/CD-style prompt-chain pipeline for preparing RAG-ready documents and structured event records.",
                    className="home-card-text"
                ),
                html.Div(
                    [
                        dbc.Button("Open Data Engineering View", href="/engineering/upload-pipeline", color="primary", className="me-2"),
                        dbc.Button("Prompt Test", href="/engineering/prompt-test", color="info", outline=True),
                    ],
                    className="home-button-row",
                ),
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


@callback(
    Output("home-tutorial-store", "data"),
    Input("home-open-tutorial", "n_clicks"),
    Input("home-tutorial-skip", "n_clicks"),
    Input("home-tutorial-prev", "n_clicks"),
    Input("home-tutorial-next", "n_clicks"),
    State("home-tutorial-store", "data"),
    prevent_initial_call=True,
)
def update_home_tutorial_state(open_clicks, skip_clicks, prev_clicks, next_clicks, store):
    store = store or {"open": True, "step": 0, "completed": False}
    step = int(store.get("step", 0))
    trigger = ctx.triggered_id
    if trigger == "home-open-tutorial":
        return {"open": True, "step": 0, "completed": False}
    if trigger == "home-tutorial-skip":
        return {**store, "open": False, "completed": True}
    if trigger == "home-tutorial-prev":
        return {**store, "open": True, "step": max(step - 1, 0)}
    if trigger == "home-tutorial-next":
        if step >= len(HOME_TUTORIAL_STEPS) - 1:
            return {**store, "open": False, "completed": True}
        return {**store, "open": True, "step": min(step + 1, len(HOME_TUTORIAL_STEPS) - 1)}
    return store


@callback(
    Output("home-tutorial-modal", "is_open"),
    Output("home-tutorial-title", "children"),
    Output("home-tutorial-progress", "children"),
    Output("home-tutorial-media", "children"),
    Output("home-tutorial-media", "style"),
    Output("home-tutorial-text", "children"),
    Output("home-tutorial-hint", "children"),
    Output("home-tutorial-prev", "disabled"),
    Output("home-tutorial-next", "children"),
    Input("home-tutorial-store", "data"),
)
def render_home_tutorial(store):
    store = store or {"open": True, "step": 0, "completed": False}
    step = min(max(int(store.get("step", 0)), 0), len(HOME_TUTORIAL_STEPS) - 1)
    item = HOME_TUTORIAL_STEPS[step]
    is_last = step == len(HOME_TUTORIAL_STEPS) - 1
    media_children, media_style = _tutorial_media(item)
    return (
        bool(store.get("open", True)),
        item["title"],
        f"Step {step + 1} of {len(HOME_TUTORIAL_STEPS)}",
        media_children,
        media_style,
        dcc.Markdown(item["text"], className="tutorial-markdown"),
        item["hint"],
        step == 0,
        "End tutorial" if is_last else "Next",
    )
