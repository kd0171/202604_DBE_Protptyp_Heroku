# Compact One-Page Engineering Pipeline

## 1. Rationale

The Data Engineering View should not behave like a set of separate tabs. The PDF upload, progress status and RAG / IE pipeline are the central workflow, so they are kept compactly at the top of the page.

The pipeline itself becomes the navigation element. Clicking a job changes the lower detail area.

## 2. Compact top area

The upper area contains:

- page title and short workflow description
- PDF upload component
- Reset button
- compact progress cards
- always-visible pipeline

The former `Upload & Pipeline` sub-tab is removed because there is only one Engineering page.

## 3. Human validation as a gate

The automated pipeline stops at `human-review` with a yellow exclamation mark.

The human validation is only completed after two levels of confirmation:

1. The analyst selects each extracted event from the dropdown and clicks **Confirm selected event**.
2. After all extracted events have been confirmed, the analyst clicks **Confirm all reviewed events**.

Only then is the session-level approval store updated.

## 4. Pipeline continuation after human validation

After **Confirm all reviewed events** is clicked:

```text
human-review: yellow ! → green check
validation-complete: runs next
save-relational-db: runs next
```

The remaining jobs continue through the same simulated timer logic as the earlier automatic jobs. This avoids making the pipeline jump immediately from human validation to completion.

## 5. Lower detail area

Clicking different jobs shows different content:

### LLM / semantic prompt-chain jobs

For semantic LLM-related jobs, the detail panel shows:

- Prompt used
- Input
- Mock output / result
- Saved artifact

Examples:

- `extract-metadata`
- `select-passages`
- `extract-events-json`
- `link-evidence`

### Non-LLM / infrastructure jobs

For non-semantic jobs, the detail panel shows:

- No LLM prompt is used
- Implementation note / to be decided
- Input
- Mock output / result
- Saved artifact

Examples:

- `upload-pdf`
- `parse-pdf`
- `chunk-document`
- `create-embeddings`
- `store-vector-db`
- `schema-precheck`
- `save-relational-db`

### Human-review job

The `human-review` job shows the embedded review interface.

### save-relational-db job

The `save-relational-db` job shows the final structured event table. Before human validation it is shown only as a preview; after human validation it represents the analysis-ready handover table.

## 6. Implementation boundary

Implemented:

- compact one-page Engineering UI
- pipeline job navigation
- embedded human validation gate
- dropdown-based event confirmation
- session-level approval store
- continuation after approval
- final structured table preview

Not implemented:

- real PDF parsing
- real LLM API calls
- real embedding generation
- real VectorDB
- real backend job orchestration
- real relational database writes


## 7. Confirm-all modal behavior

The `Confirm all reviewed events` button now supports two paths:

1. **All events were individually confirmed**  
   The Human Review gate is approved immediately and the pipeline continues.

2. **Some events were not individually confirmed**  
   A modal dialog appears. The user can either go back and review the missing records or click **Confirm all anyway**.

If **Confirm all anyway** is clicked, the PoC treats all event records as reviewed for the current browser session. The approval payload records that this was a forced confirmation and stores the list of records that had not been individually confirmed.


### Modal initialization note

The confirm-all modal should not appear merely because the `human-review` job was clicked and the Human Review panel was rendered. It opens only when the user explicitly clicks **Confirm all reviewed events** while some individual events are still unconfirmed.
