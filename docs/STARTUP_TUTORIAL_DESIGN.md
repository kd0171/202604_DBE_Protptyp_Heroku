# Startup Tutorial Design

## 1. Purpose

The Data Engineering View contains several concepts that are not immediately obvious for first-time users:

- PDF upload
- common preprocessing
- RAG branch
- IE branch
- prompt-chain inspection
- human validation as a pipeline gate
- individual and bulk confirmation
- final relational event table

For this reason, the app now shows a startup tutorial when the Engineering page is opened for the first time in a browser session.

## 2. Recommended format

The tutorial is implemented as a large modal overlay. This is preferable to a small tooltip in the lower corner because the workflow is conceptual and needs a short guided explanation before the user starts interacting with the PoC.

The modal contains:

- step title
- step counter
- placeholder area for a future GIF or screenshot
- short explanation
- user hint
- Previous button
- Next / Finish button
- Skip tutorial button

A `Tutorial` button in the compact top control area allows the user to reopen the tutorial.

## 3. Number of steps

The tutorial currently uses 8 steps:

1. **Overview**  
   Explains the one-page workflow and the role of the upper and lower areas.

2. **Upload PDF**  
   Explains that the user can upload a PDF to start the simulated pipeline.

3. **Read the pipeline**  
   Explains green checks, running jobs and the yellow human-validation gate.

4. **Click pipeline jobs**  
   Explains that the pipeline itself acts as the navigation element.

5. **Inspect prompt-chain steps**  
   Explains that semantic LLM-related jobs show prompts, inputs, outputs and saved artifacts.

6. **Human validation gate**  
   Explains why the pipeline stops at `human-review`.

7. **Confirm records individually or all at once**  
   Explains dropdown-based individual confirmation and the confirm-all modal.

8. **Check final RDB output**  
   Explains the final `save-relational-db` table and its handover to the Data Analysis View.

Eight steps is a reasonable upper limit. Fewer steps would merge important concepts and make the workflow harder to understand. More than eight steps would make the tutorial feel too long.

## 4. GIF / screenshot strategy

GIFs are useful but not required for the first implementation. The current app uses placeholders that can later be replaced with GIFs or screenshots.

Recommended GIFs:

- PDF upload
- Pipeline progress and yellow human-review gate
- Clicking a prompt-chain job
- Human review dropdown confirmation
- Confirm-all modal
- Final relational table view

GIFs should be short, ideally 3–8 seconds each. They should show one interaction only. Long screen recordings should be avoided.

## 5. Implementation notes

The tutorial state is stored in a session-level `dcc.Store`:

```text
id="ep-tutorial-store"
storage_type="session"
```

This means the tutorial can be skipped for the current browser session, while still being reopenable through the Tutorial button.

The tutorial is intentionally independent from the pipeline state. Skipping the tutorial does not start the pipeline, approve validation, or change any data.


## 6. Upload-triggered pipeline start

The previous demo button was removed because it was confusing to run the pipeline without an uploaded document. The simulated pipeline now starts automatically after a PDF is selected in the upload component. The Reset button remains available for restarting the UI state.

The Tutorial button is placed between the page title and the PDF upload area so the user can reopen the onboarding flow before starting the upload.
