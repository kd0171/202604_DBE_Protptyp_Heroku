
import dash
from dash import html, Input, Output, callback
import dash_bootstrap_components as dbc
from utils import load_data, compact_table, data_note, LLM_EVENT_COLUMNS

dash.register_page(__name__, path="/engineering/save-database", name="Save to Database")
data = load_data()
events = data["events"]

SQL_EXAMPLE = """SELECT country, event_type, COUNT(*) AS event_count
FROM llm_extracted_company_events
WHERE event_presence = 'yes'
GROUP BY country, event_type
ORDER BY event_count DESC;"""

def layout():
    ready = events[events["validation_status"].isin(["passed","warning"])].copy()
    verified = events[events["human_verified"] == True].copy()
    return html.Div([
        html.H2("Save to Database", className="page-title"),
        html.P("After validation and human review, event records are saved as normal relational rows. Click the save button to display the database table preview.", className="page-lead"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Records ready to save", className="kpi-title"),
                html.Div(str(len(ready)), className="kpi-value"),
                html.Div("passed or warning validation status", className="kpi-sub")
            ]), className="kpi-card"), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Human verified records", className="kpi-title"),
                html.Div(str(len(verified)), className="kpi-value"),
                html.Div("used for high-confidence mode", className="kpi-sub")
            ]), className="kpi-card"), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div("Target table", className="kpi-title"),
                html.Div("llm_extracted_company_events", className="kpi-value-small"),
                html.Div("relational event table", className="kpi-sub"),
                dbc.Button("Save approved records to database", id="sd-save", color="primary", className="mt-3", n_clicks=0)
            ]), className="kpi-card"), md=6),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Database table preview"),
                dbc.CardBody(html.Div(id="sd-db-preview"))
            ]), md=8),
            dbc.Col(dbc.Card([
                dbc.CardHeader("SQL query example"),
                dbc.CardBody(html.Pre(SQL_EXAMPLE, className="sql-box"))
            ]), md=4)
        ], className="chart-row")
    ])

@callback(
    Output("sd-db-preview", "children"),
    Input("sd-save", "n_clicks")
)
def show_saved_table(n_clicks):
    if not n_clicks:
        return dbc.Alert("Click Save approved records to database to display saved records.", color="light")
    ready = events[events["validation_status"].isin(["passed","warning"])].copy()
    cols = ["event_id","company_name","event_type","country","city","product_category","status","source_text","human_verified"]
    return html.Div([
        dbc.Alert(f"{len(ready)} records saved to llm_extracted_company_events.", color="success"),
        data_note("llm_extracted_company_events table", llm_note=True),
        compact_table(ready, cols, llm_columns=LLM_EVENT_COLUMNS, page_size=7)
    ])
