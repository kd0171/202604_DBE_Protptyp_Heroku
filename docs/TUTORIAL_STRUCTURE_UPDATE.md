# Tutorial structure update

This update reorganizes tutorial media assets and adds tutorials to the Home and Prompt Test pages.

## Asset folders

```text
assets/tutorial/
  data_engineering/
    01_download_sample_pdf.gif
    02_upload_sample_pdf.gif
    03_upload_validation_note.gif
    04_pipeline_overview.gif
    05_pipeline_prompt_output.gif
    06_human_verification.gif
    07_verified_data_saved_to_db.gif
  home/
    HomePage.gif
  prompt_test/
    PromptTest_1_SamplePDFDownload.gif
    PromptTest_2_CopyPromptAddPDFGetJSON.gif
    PromptTest_3_4thPromptGetTable.gif
```

## Implemented tutorials

- Home page tutorial with two steps: welcome and navigation GIF.
- Prompt Test tutorial with three GIF-based steps: sample PDF download, prompt copying/external LLM JSON generation, and final JSON-to-table preview.
- Data Engineering tutorial paths were updated to use the `assets/tutorial/data_engineering/` folder.

If Home or Prompt Test GIFs are not yet present, the app shows a clear placeholder with the expected file path instead of rendering a broken image.
