# Data Analysis Tutorial Update

## Summary

This update adds a short tutorial to the Data Analysis View / Analysis Workspace.

## GIF placement

The tutorial expects the following files:

```text
assets/tutorial/data_analysis/DataAnalysis_1_ModeChange.gif
assets/tutorial/data_analysis/DataAnalysis_2_AskQuestion.gif
```

If these files are not present, the app shows a placeholder with the expected path.

## Tutorial steps

1. **Switch between Dashboard and Interactive Mode**
   - Explains that the Data Analysis View has Dashboard Mode and Interactive Mode.
   - Uses `DataAnalysis_1_ModeChange.gif`.

2. **Ask a supported example question**
   - Explains that a supported example question can be pasted into Interactive Mode.
   - Shows that the prototype displays a prepared answer, related plot, evidence records and validation note.
   - Clarifies that the prototype does not call a live LLM API and only predefined example questions are connected to prepared outputs.
   - Uses `DataAnalysis_2_AskQuestion.gif`.

## Folder structure

Tutorial assets are now separated by page:

```text
assets/tutorial/home/
assets/tutorial/data_engineering/
assets/tutorial/prompt_test/
assets/tutorial/data_analysis/
```
