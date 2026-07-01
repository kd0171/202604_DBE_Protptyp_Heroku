import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils import load_data, compact_table, data_note


dash.register_page(__name__, path="/analysis/competitive-scorecard", name="Competitive Scorecard")

data = load_data()
axis_scores = data["ci_axis_scores"].copy()
score_details = data["ci_score_details"].copy()
scoring_items = data["ci_scoring_items"].copy()
axis_weights = data["ci_axis_weights"].copy()
indicators = data["ci_indicators"].copy()
overall_scores = data["ci_overall_scores"].copy()
coverage = data["ci_axis_coverage"].copy()
gaps = data["ci_data_gaps"].copy()

AXIS_ORDER = [
    "finance", "risk", "sustainability", "operations", "products", "regulation", "investment"
]
DISPLAY_AXIS = dict(zip(axis_scores["axis"], axis_scores["display_axis"])) if not axis_scores.empty else {}
AXIS_OPTIONS = [
    {"label": DISPLAY_AXIS.get(axis, axis.title()), "value": axis}
    for axis in AXIS_ORDER
]
COMPANY_OPTIONS = [
    {"label": r.company_name, "value": r.company_id}
    for r in overall_scores.sort_values("company_name").itertuples()
]
DEFAULT_COMPANIES = [o["value"] for o in COMPANY_OPTIONS]


def _safe_companies(selected):
    selected = selected or DEFAULT_COMPANIES
    known = set(axis_scores["company_id"].unique())
    return [x for x in selected if x in known] or DEFAULT_COMPANIES


def _axis_label(axis):
    return DISPLAY_AXIS.get(axis, axis.title())


def _kpi_cards(selected_companies):
    selected_companies = _safe_companies(selected_companies)
    df = overall_scores[overall_scores["company_id"].isin(selected_companies)].copy()
    if df.empty:
        return dbc.Alert("No score data available.", color="light")
    cards = []
    for r in df.sort_values("overall_score_1_5", ascending=False).itertuples():
        cards.append(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(r.company_name, className="kpi-title"),
                        html.Div(f"{r.overall_score_1_5:.2f} / 5", className="kpi-value-small"),
                        html.Div(f"Evidence confidence: {r.avg_confidence:.2f}", className="kpi-sub"),
                    ]),
                    className="kpi-card score-kpi-card",
                ),
                md=2,
            )
        )
    return dbc.Row(cards, className="g-2")


def _make_radar(selected_companies):
    selected_companies = _safe_companies(selected_companies)
    df = axis_scores[axis_scores["company_id"].isin(selected_companies)].copy()
    fig = go.Figure()
    labels = [_axis_label(axis) for axis in AXIS_ORDER]
    for company_id, g in df.groupby("company_id"):
        g = g.set_index("axis").reindex(AXIS_ORDER).reset_index()
        scores = g["score_1_5"].tolist()
        fig.add_trace(
            go.Scatterpolar(
                r=scores + scores[:1],
                theta=labels + labels[:1],
                fill="toself",
                name=g["company_name"].dropna().iloc[0],
                hovertemplate="%{theta}<br>Score: %{r:.2f}/5<extra>%{fullData.name}</extra>",
            )
        )
    fig.update_layout(
        height=560,
        margin=dict(l=30, r=30, t=30, b=30),
        polar=dict(radialaxis=dict(visible=True, range=[0, 5], tickvals=[1,2,3,4,5])),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    return fig


def _make_axis_bar(selected_companies, selected_axis):
    selected_companies = _safe_companies(selected_companies)
    df = axis_scores[(axis_scores["company_id"].isin(selected_companies)) & (axis_scores["axis"] == selected_axis)].copy()
    df = df.sort_values("score_1_5", ascending=True)
    fig = px.bar(
        df,
        x="score_1_5",
        y="company_name",
        orientation="h",
        text="score_1_5",
        hover_data=["score_confidence"],
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=35, t=10, b=10),
        xaxis_title=f"{_axis_label(selected_axis)} score, 1-5",
        yaxis_title="",
        xaxis=dict(range=[0, 5]),
        showlegend=False,
    )
    return fig


def _make_score_matrix(selected_companies):
    selected_companies = _safe_companies(selected_companies)
    df = axis_scores[axis_scores["company_id"].isin(selected_companies)].copy()
    matrix = df.pivot(index="company_name", columns="display_axis", values="score_1_5")
    ordered_cols = [_axis_label(a) for a in AXIS_ORDER if _axis_label(a) in matrix.columns]
    matrix = matrix[ordered_cols]
    fig = px.imshow(
        matrix,
        text_auto=".2f",
        aspect="auto",
        zmin=1,
        zmax=5,
        labels=dict(x="Axis", y="Company", color="Score"),
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
    return fig


def _score_detail_table(selected_companies, selected_axis):
    selected_companies = _safe_companies(selected_companies)
    df = score_details[(score_details["company_id"].isin(selected_companies)) & (score_details["axis"] == selected_axis)].copy()
    cols = [
        "company_name", "display_axis", "scoring_item", "item_weight", "item_score_1_5",
        "weighted_points", "item_rationale", "evidence_record_ids"
    ]
    return compact_table(df, cols, page_size=12)


def _evidence_table(selected_companies, selected_axis):
    selected_companies = _safe_companies(selected_companies)
    df = indicators[(indicators["company_id"].isin(selected_companies)) & (indicators["axis"] == selected_axis)].copy()
    cols = [
        "record_id", "company_name", "axis", "metric_name", "period", "value_numeric",
        "value_text", "unit", "source_type", "source_document", "source_page", "confidence", "evidence_text"
    ]
    return compact_table(df, cols, page_size=8)


def _coverage_table(selected_companies):
    selected_companies = _safe_companies(selected_companies)
    df = coverage[coverage["company_id"].isin(selected_companies)].copy()
    cols = ["company_name", "axis", "records_total", "quantitative_records", "qualitative_records", "avg_confidence", "coverage_status", "notes"]
    return compact_table(df, cols, page_size=10)


def _gap_cards(selected_companies):
    selected_companies = _safe_companies(selected_companies)
    df = gaps[gaps["company_id"].isin(selected_companies)].copy()
    if df.empty:
        return dbc.Alert("No critical data gaps recorded for the selected companies.", color="light")
    cards = []
    for r in df.itertuples():
        cards.append(
            dbc.Col(
                dbc.Alert([
                    html.Strong(r.company_id.replace("_", " ").title()),
                    html.Div(r.gap),
                    html.Small(r.impact),
                ], color="warning", className="mb-2"),
                md=6,
            )
        )
    return dbc.Row(cards, className="g-2")


def layout():
    return html.Div([
        html.H2("Competitive Intelligence Scorecard", className="page-title"),
        html.P(
            "This view turns extracted official-document evidence into an explainable radar scorecard. "
            "Scores are rule-based and editable; they are not LLM-generated strategic judgements.",
            className="page-lead",
        ),
        dbc.Alert(
            "Interpretation rule: higher score is better. For the risk axis, the displayed score means risk resilience / lower concern, not higher risk severity.",
            color="info",
            className="mb-3",
        ),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Companies"),
                dcc.Dropdown(
                    id="cs-companies",
                    options=COMPANY_OPTIONS,
                    value=DEFAULT_COMPANIES,
                    multi=True,
                    clearable=False,
                ),
            ])), md=7),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Axis for evidence tables"),
                dcc.Dropdown(
                    id="cs-axis",
                    options=AXIS_OPTIONS,
                    value="finance",
                    clearable=False,
                ),
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Label("Score basis"),
                html.Div("Official PDFs + official web supplements", className="kpi-value-small"),
                html.Div("CSV-backed scoring model", className="kpi-sub"),
            ])), md=2),
        ], className="control-row"),
        html.Div(id="cs-kpis", className="mb-3"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Company radar scorecard"),
                dbc.CardBody([
                    data_note("ci_axis_scores.csv + ci_weighted_score_details.csv"),
                    dcc.Graph(id="cs-radar"),
                ]),
            ]), md=8),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Scoring logic"),
                dbc.CardBody([
                    html.P("The radar aggregates equally weighted axes. Each axis is built from weighted sub-items shown below.", className="data-note"),
                    dbc.Button("Show / hide weighting table", id="cs-toggle-weights", color="secondary", outline=True, size="sm", className="mb-2"),
                    dbc.Collapse(
                        html.Div([
                            html.Div("Axis weights", className="section-label"),
                            compact_table(axis_weights, ["display_axis", "axis_weight", "axis_weight_rationale"], page_size=7),
                            html.Div("Sub-item weights", className="section-label mt-3"),
                            compact_table(scoring_items, ["display_axis", "scoring_item", "weight", "weight_rationale"], page_size=12),
                        ]),
                        id="cs-weight-collapse",
                        is_open=False,
                    ),
                ]),
            ], className="score-logic-card"), md=4),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Selected axis ranking"), dbc.CardBody(dcc.Graph(id="cs-axis-bar"))]), md=5),
            dbc.Col(dbc.Card([dbc.CardHeader("Score matrix"), dbc.CardBody(dcc.Graph(id="cs-score-matrix"))]), md=7),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Weighted score detail for selected axis"),
                dbc.CardBody([
                    data_note("ci_weighted_score_details.csv"),
                    html.Div(id="cs-score-detail-table"),
                ]),
            ]), md=12),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Evidence records behind selected axis"),
                dbc.CardBody([
                    data_note("ci_extracted_indicators_long.csv"),
                    html.Div(id="cs-evidence-table"),
                ]),
            ]), md=12),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Coverage and confidence"),
                dbc.CardBody([
                    data_note("ci_axis_coverage_summary.csv"),
                    html.Div(id="cs-coverage-table"),
                ]),
            ]), md=7),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Data gaps and warnings"),
                dbc.CardBody(html.Div(id="cs-gap-cards")),
            ]), md=5),
        ], className="chart-row"),
    ])


@callback(
    Output("cs-weight-collapse", "is_open"),
    Input("cs-toggle-weights", "n_clicks"),
    State("cs-weight-collapse", "is_open"),
)
def toggle_weight_table(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("cs-kpis", "children"),
    Output("cs-radar", "figure"),
    Output("cs-axis-bar", "figure"),
    Output("cs-score-matrix", "figure"),
    Output("cs-score-detail-table", "children"),
    Output("cs-evidence-table", "children"),
    Output("cs-coverage-table", "children"),
    Output("cs-gap-cards", "children"),
    Input("cs-companies", "value"),
    Input("cs-axis", "value"),
)
def update_scorecard(selected_companies, selected_axis):
    selected_axis = selected_axis or "finance"
    selected_companies = _safe_companies(selected_companies)
    return (
        _kpi_cards(selected_companies),
        _make_radar(selected_companies),
        _make_axis_bar(selected_companies, selected_axis),
        _make_score_matrix(selected_companies),
        _score_detail_table(selected_companies, selected_axis),
        _evidence_table(selected_companies, selected_axis),
        _coverage_table(selected_companies),
        _gap_cards(selected_companies),
    )
