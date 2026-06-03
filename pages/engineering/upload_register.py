
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from utils import load_data, compact_table, data_note

dash.register_page(__name__, path="/engineering/upload-register", name="Source Registration")
data = load_data()
sources = data["sources"]
companies = data["companies"]
required_documents = data["required_documents"]

def find_document_by_filename(filename):
    if not filename:
        return None
    normalized = filename.strip()
    for doc in required_documents:
        if normalized == doc["required_file_name"]:
            return doc
    return None

def layout():
    return html.Div([
        html.H2("Document Source Registration", className="page-title"),
        html.P(
            "Upload an official company PDF. The application reads the document metadata, fills the registration fields, and lets the analyst confirm or correct the values before registering the document as an extraction source.",
            className="page-lead"
        ),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Required PDF documents"),
                dbc.CardBody([
                    html.P("Use the following official PDF files and file names for this workflow."),
                    compact_table(
                        __import__("pandas").DataFrame(required_documents),
                        ["company_name","document_title","source_site","required_file_name"],
                        page_size=5
                    )
                ])
            ]), md=12)
        ], className="chart-row"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("1. Upload official PDF"),
                dbc.CardBody([
                    dcc.Upload(
                        id="pdf-upload",
                        children=html.Div(["Drag and drop or select a PDF file"]),
                        className="upload-box",
                        multiple=False
                    ),
                    html.Div(id="ur-upload-status", className="status-text"),
                    dcc.Store(id="ur-uploaded-filename")
                ])
            ]), md=5),

            dbc.Col(dbc.Card([
                dbc.CardHeader("2. Confirm detected metadata"),
                dbc.CardBody([
                    dbc.Label("Source ID"),
                    dbc.Input(id="ur-source-id", type="text"),
                    dbc.Label("Company", className="mt-2"),
                    dcc.Dropdown(
                        id="ur-company",
                        options=[{"label": r.company_name, "value": r.company_id} for r in companies.itertuples()],
                        value=None
                    ),
                    dbc.Label("Document type", className="mt-2"),
                    dcc.Dropdown(
                        id="ur-doc-type",
                        options=[{"label": x, "value": x} for x in ["annual_report","sustainability_report","investor_presentation","official_press_release"]],
                        value=None
                    ),
                    dbc.Label("Document title", className="mt-2"),
                    dbc.Input(id="ur-doc-title", type="text"),
                    dbc.Label("Publication year", className="mt-2"),
                    dbc.Input(id="ur-year", type="number"),
                    dbc.Label("Language", className="mt-2"),
                    dbc.Input(id="ur-language", type="text"),
                    dbc.Button("Register document as extraction source", id="ur-register", color="primary", className="mt-3", n_clicks=0),
                    html.Div(id="ur-register-status", className="status-text mt-2")
                ])
            ]), md=7),
        ], className="chart-row"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Registered extraction sources"),
                dbc.CardBody(html.Div(id="ur-source-table"))
            ]), md=12)
        ], className="chart-row")
    ])

@callback(
    Output("ur-upload-status", "children"),
    Output("ur-uploaded-filename", "data"),
    Output("ur-source-id", "value"),
    Output("ur-company", "value"),
    Output("ur-doc-type", "value"),
    Output("ur-doc-title", "value"),
    Output("ur-year", "value"),
    Output("ur-language", "value"),
    Input("pdf-upload", "filename"),
    prevent_initial_call=False
)
def auto_detect_metadata(filename):
    if not filename:
        return (
            "Upload one of the listed official PDF files to detect document metadata.",
            None, "", None, None, "", None, ""
        )

    doc = find_document_by_filename(filename)
    if not doc:
        return (
            f"Uploaded file: {filename}. The file name is not in the registered document list. Please rename it to one of the required file names or enter the metadata manually.",
            filename, "", None, None, "", None, ""
        )

    return (
        f"Uploaded file: {filename}. Document metadata has been detected and filled below.",
        filename,
        doc["source_id"],
        doc["company_id"],
        doc["document_type"],
        doc["document_title"],
        doc["publication_year"],
        doc["language"]
    )

@callback(
    Output("ur-register-status", "children"),
    Output("ur-source-table", "children"),
    Input("ur-register", "n_clicks"),
    State("ur-source-id", "value"),
    State("ur-company", "value"),
    State("ur-doc-type", "value"),
    State("ur-doc-title", "value"),
    State("ur-year", "value"),
    State("ur-language", "value"),
    State("ur-uploaded-filename", "data"),
    prevent_initial_call=False
)
def register_source(n_clicks, source_id, company, doc_type, doc_title, year, language, filename):
    if not n_clicks:
        return (
            "After uploading and confirming metadata, click Register document as extraction source.",
            dbc.Alert("No document has been registered yet.", color="light")
        )

    company_name = companies.loc[companies["company_id"].eq(company), "company_name"].iloc[0] if company else ""
    registered = sources.copy()
    new_row = {
        "source_id": source_id,
        "company_id": company,
        "company_name": company_name,
        "document_type": doc_type,
        "document_title": doc_title,
        "publication_year": year,
        "language": language,
        "url_or_file": filename or "",
        "source_owner": company_name,
        "human_selected": True,
        "pipeline_status": "registered",
        "notes": "Registered by analyst"
    }

    # Replace existing source_id in the displayed table or append it.
    if source_id in set(registered["source_id"]):
        for key, value in new_row.items():
            if key in registered.columns:
                registered.loc[registered["source_id"].eq(source_id), key] = value
    else:
        registered = __import__("pandas").concat([registered, __import__("pandas").DataFrame([new_row])], ignore_index=True)

    status = f"Registered {source_id} for {company_name}. This document can now be selected on the LLM Extraction page."

    return (
        status,
        html.Div([
            data_note("document_sources.csv"),
            compact_table(
                registered,
                ["source_id","company_name","document_type","document_title","publication_year","language","url_or_file","human_selected","pipeline_status"],
                page_size=6
            )
        ])
    )
