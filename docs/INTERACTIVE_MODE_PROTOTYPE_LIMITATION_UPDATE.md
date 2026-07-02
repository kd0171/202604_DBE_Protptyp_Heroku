# Interactive Mode prototype limitation update

The Analysis Workspace interactive mode was revised so that the question field is a free-text input rather than a dropdown-based selector.

The current predefined questions are displayed only as example questions. In this prototype, answers are generated only if the typed question exactly matches one of those examples. Other free-text questions intentionally do not generate an answer because the prototype does not implement live LLM calls, vector retrieval or dynamic answer generation.

This design makes the intended user interaction visible without overstating the technical scope of the prototype.
