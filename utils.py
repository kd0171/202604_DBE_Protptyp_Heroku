
from pathlib import Path
import pandas as pd
from dash import dash_table, html
import dash_bootstrap_components as dbc
import json

DATA_DIR = Path(__file__).parent / "data"

LLM_EVENT_COLUMNS = {
    "event_type", "event_presence", "country", "city", "site_name",
    "business_segment", "product_category", "sugar_type", "production_type",
    "investment_amount", "investment_currency", "capacity_change", "capacity_value",
    "capacity_unit", "target_year", "start_year", "status", "source_text",
    "extraction_confidence"
}

def _read_optional_csv(filename):
    path = DATA_DIR / filename
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

def load_data():
    return {
        "companies": pd.read_csv(DATA_DIR / "companies.csv"),
        "market": pd.read_csv(DATA_DIR / "market_indicators.csv"),
        "country_stats": pd.read_csv(DATA_DIR / "country_sugar_stats.csv"),
        "sites": pd.read_csv(DATA_DIR / "company_sites.csv"),
        "sources": pd.read_csv(DATA_DIR / "document_sources.csv"),
        "events": pd.read_csv(DATA_DIR / "llm_extracted_company_events.csv"),
        "pipeline_steps": pd.read_csv(DATA_DIR / "pipeline_steps.csv"),
        "interactive_queries": json.loads((DATA_DIR / "interactive_queries.json").read_text(encoding="utf-8")),
        "required_documents": json.loads((DATA_DIR / "required_documents.json").read_text(encoding="utf-8")),
        # Competitive scorecard data generated from uploaded official documents
        # and clearly separated official website supplements.
        "ci_indicators": _read_optional_csv("ci_extracted_indicators_long.csv"),
        "ci_axis_scores": _read_optional_csv("ci_axis_scores.csv"),
        "ci_score_details": _read_optional_csv("ci_weighted_score_details.csv"),
        "ci_scoring_items": _read_optional_csv("ci_scoring_items.csv"),
        "ci_axis_weights": _read_optional_csv("ci_axis_weights.csv"),
        "ci_overall_scores": _read_optional_csv("ci_overall_scores.csv"),
        "ci_axis_coverage": _read_optional_csv("ci_axis_coverage_summary.csv"),
        "ci_data_gaps": _read_optional_csv("ci_data_gaps_and_warnings.csv"),
        "ci_document_inventory": _read_optional_csv("ci_document_inventory.csv"),
        "ci_supplement_sources": _read_optional_csv("ci_official_site_supplement_sources.csv"),
    }

def capacity_size(series):
    mapping = {"small":7, "medium":11, "large":16, "unknown":9}
    return series.map(mapping).fillna(9)

def compact_table(df, columns=None, llm_columns=None, page_size=7, table_id=None, editable=False):
    if df is None or df.empty:
        return dbc.Alert("No data for the current selection.", color="light")
    show = df.copy()
    if columns:
        show = show[[c for c in columns if c in show.columns]]
    show = show.replace({pd.NA:"", None:""}).fillna("")
    llm_columns = set(llm_columns or [])
    style_data_conditional = []
    for col in show.columns:
        if col in llm_columns:
            style_data_conditional.append({
                "if": {"column_id": col},
                "backgroundColor": "#fff3b0",
                "color": "#1f2933",
            })
    kwargs = dict(
        data=show.to_dict("records"),
        columns=[{"name": c, "id": c, "editable": editable} for c in show.columns],
        page_size=page_size,
        sort_action="native",
        filter_action="native",
        editable=editable,
        style_table={"overflowX": "auto"},
        style_cell={
            "fontFamily": "Segoe UI, Arial, sans-serif",
            "fontSize": "12px",
            "padding": "6px",
            "textAlign": "left",
            "maxWidth": "280px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={
            "backgroundColor": "#eef2f7",
            "fontWeight": "700",
            "color": "#0b3b5b",
        },
        style_data_conditional=style_data_conditional,
    )
    if table_id is not None:
        kwargs["id"] = table_id
    return dash_table.DataTable(**kwargs)

def data_note(source_file, llm_note=False):
    if llm_note:
        return html.Div([
            html.Span("Data used: ", className="data-note-label"),
            html.Code(source_file),
            html.Span(" | Yellow cells = LLM-extracted fields", className="llm-note"),
        ], className="data-note")
    return html.Div([
        html.Span("Data used: ", className="data-note-label"),
        html.Code(source_file),
        html.Span(" | Public / curated non-LLM data", className="public-note"),
    ], className="data-note")

def country_score(country_stats, sites, events):
    stats = country_stats.copy()
    site_counts = sites.groupby("country").agg(
        site_count=("site_id","count"),
        company_count=("company_id","nunique")
    ).reset_index()
    event_counts = events[events["event_presence"].eq("yes")].groupby("country").agg(
        event_count=("event_id","count")
    ).reset_index()
    df = stats.merge(site_counts, on="country", how="left").merge(event_counts, on="country", how="left")
    for col in ["site_count", "company_count", "event_count"]:
        df[col] = df[col].fillna(0)
    def norm(s):
        if s.max() == s.min():
            return s*0
        return (s - s.min()) / (s.max() - s.min())
    df["production_score"] = norm(df["sugar_production"])
    df["site_score"] = norm(df["site_count"])
    df["event_score"] = norm(df["event_count"])
    df["regional_activity_score"] = (0.45*df["production_score"] + 0.30*df["site_score"] + 0.25*df["event_score"]).round(3)
    return df

def match_query(user_query, query_configs):
    """
    Select the best predefined intent by keyword score.
    This prevents broad intents such as "competitor" from capturing
    more specific questions such as "bioethanol competitor activities".
    """
    q = (user_query or "").lower()
    best_item = query_configs[0]
    best_score = -1
    for item in query_configs:
        score = 0
        for kw in item.get("matched_keywords", []):
            kw_l = kw.lower()
            if kw_l and kw_l in q:
                # Longer / more specific keywords should count more.
                score += max(1, len(kw_l.split()))
                if len(kw_l) >= 10:
                    score += 1
        # Exact example question match is strongest.
        for ex in item.get("example_questions", []):
            if ex.lower().strip() == q.strip():
                score += 100
        if score > best_score:
            best_score = score
            best_item = item
    return best_item

def apply_interactive_filters(events, filters):
    df = events.copy()
    if not filters:
        return df
    if filters.get("exclude_company"):
        df = df[df["company_id"] != filters["exclude_company"]]
    if filters.get("country"):
        df = df[df["country"] == filters["country"]]
    if filters.get("event_presence"):
        df = df[df["event_presence"] == filters["event_presence"]]
    if filters.get("product_category"):
        df = df[df["product_category"] == filters["product_category"]]
    if filters.get("event_type"):
        ev = filters["event_type"]
        if isinstance(ev, list):
            df = df[df["event_type"].isin(ev)]
        else:
            df = df[df["event_type"] == ev]
    return df
