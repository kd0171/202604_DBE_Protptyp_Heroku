# One-Page Data Engineering View Design

## 1. Design decision

The Data Engineering part of the PoC should be understood as one continuous workflow rather than as several isolated pages. Therefore, the application uses a one-page layout:

```text
PDF Upload
→ always-visible pipeline
→ dynamic detail area below the pipeline
```

The pipeline remains visible at the top of the page. When the user clicks a job, the lower detail area changes. This makes the pipeline itself the main navigation element of the Data Engineering View.

The separate **Data Analysis View** remains unchanged and separate.

---

## 2. Pipeline structure

The pipeline is organized as follows:

```text
Source Intake
→ Text Preparation
→ split
   ├─ RAG Indexing
   │  → Retrieval Ready
   │
   └─ Event Extraction
      → Human Review & Validation
      → Structured Storage
```

The first two phases are common preprocessing steps. After the cleaned text is available, the workflow splits into a RAG branch and an IE branch.

---

## 3. Why Human Review is embedded below the pipeline

In this PoC, the main manual action is **human validation**. Therefore, it is more intuitive to show the Human Review interface as the detail panel of the `human-review` job instead of forcing the user into a separate page.

Expected behavior:

1. The user uploads a PDF or starts the demo pipeline.
2. The automated part runs until `human-review`.
3. The `human-review` job is shown with a yellow exclamation mark.
4. A warning below the pipeline asks the user to check the extracted data.
5. The lower detail area displays the Human Review UI.
6. After the user clicks **Approve human validation**, the session store is updated.
7. The pipeline changes from the yellow gate to green completion.
8. The final `save-relational-db` job can be clicked to inspect the final structured table.

This represents the business rule that machine validation alone is not sufficient. Validation becomes complete only after human review.

---

## 4. What each clicked job should display

The lower detail area depends on the selected job.

### 4.1 LLM / semantic prompt-chain jobs

For jobs where an LLM semantically interprets text, the app should show:

```text
Prompt used
Input
Mock output / result
Saved artifact
```

These jobs include:

- `extract-metadata`
- `select-passages`
- `extract-events-json`
- `link-evidence`

These are the most important steps for transparency because they determine how unstructured text becomes metadata, selected passages, structured events, and evidence links.

### 4.2 Non-LLM infrastructure or data-processing jobs

For jobs that are not part of the semantic prompt chain, the app should not pretend that a prompt exists. Instead, it shows:

```text
No LLM prompt is used.
Implementation note / to be decided.
Input
Saved artifact
Mock output / result
```

Examples:

- `upload-pdf`
- `register-source`
- `parse-pdf`
- `extract-clean-text`
- `chunk-document`
- `create-embeddings`
- `store-vector-db`
- `schema-precheck`
- `save-relational-db`

This distinction is important because not every part of the system is an LLM task. Some steps are ordinary data engineering or backend infrastructure tasks.

---

## 5. Human Review detail panel

When `human-review` is clicked, the lower panel shows a review interface:

```text
Selected extracted event
Evidence text
Editable event fields
Approve human validation button
```

The user checks whether the extracted event data is supported by the evidence text. After approval, the global session store records the approval state, and the pipeline is displayed as completed for the current session.

---

## 6. Final Structured Storage panel

When `save-relational-db` is clicked, the lower panel shows the final structured event table.

If human validation has not been approved yet, the panel explains that structured storage is still blocked and the table is only a preview.

After approval, the table is shown as the final structured event output handed over to the separate Data Analysis View.

---

## 7. Implementation boundary

Implemented in the current frontend PoC:

- PDF upload UI
- Always-visible RAG / IE pipeline
- Clickable jobs
- Prompt-chain detail panels
- Human Review embedded as a pipeline detail panel
- Session-level approval with `dcc.Store`
- Final structured table preview

Not implemented in the current frontend PoC:

- Real PDF parsing
- Real LLM API calls
- Real embedding generation
- Real VectorDB storage
- Real RAG retrieval
- Backend job orchestration
- Real relational database writes
- Authentication and audit logging

The purpose is to demonstrate the business and information architecture of the workflow, not to implement a production backend.
