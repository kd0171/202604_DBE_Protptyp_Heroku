# Data Engineering changes implemented

## Scope

The existing one-page Data Engineering layout was kept as far as possible. The changes focus on the Upload & Pipeline page.

## Pipeline phase display

Each pipeline phase card now shows a small phase-specific context box while the simulated pipeline progresses. The box displays the currently relevant artifact for that phase, for example:

- source intake → document registry / metadata
- text preparation → cleaned text blocks
- RAG indexing → chunks / embeddings
- retrieval-ready → vector collection placeholder
- event extraction → candidate passages / extracted JSON / evidence
- human validation → review decisions
- structured storage → final validated event table

This makes the green check progression easier to understand because the user sees not only that a job is completed, but also what artifact belongs to that phase.

## Human review save and confirm logic

Human review now uses browser-side Dash stores instead of any server-side database.

Stores used on the Upload & Pipeline page:

- `ep-review-records-store`: session-level edited event records
- `ep-confirmed-events`: individually confirmed event IDs
- `ep-required-events`: required event IDs for the current review queue
- `global-human-validation-store`: global session-level approval payload shared with the pipeline gate

The selected event can now be handled in two separate ways:

1. `Save edits only` saves the current form values into `ep-review-records-store` but does not confirm the event.
2. `Save & confirm selected event` saves the current form values and marks that event as individually confirmed.

The existing separation between individual confirmation and full-batch confirmation is preserved:

- `Save & confirm selected event` confirms one selected event.
- `Confirm all reviewed events` releases the full Human Review gate only after all required events are confirmed.
- If not all events are individually confirmed, the existing modal still appears and the user can either return or force-confirm all.

## Render deployment logic

No database is required. The implementation avoids server-side persistence and keeps review data in the browser session store. After the Human Review gate is approved, the reviewed records are copied into `global-human-validation-store` as `reviewed_records`.

For export, the Structured Storage phase now provides `Download validated CSV`. This gives the user a portable output artifact without relying on Render's ephemeral filesystem or an external database.

## Main files changed

- `pages/engineering/upload_pipeline.py`
- `assets/style.css`
