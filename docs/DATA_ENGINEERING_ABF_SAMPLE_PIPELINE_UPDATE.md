# Data Engineering ABF Sample Pipeline Update

The Engineering View now uses **ABF Annual Report 2025** as the explicit sample PDF. This document was selected because it contains a compact set of strategically relevant competitor signals for Nordzucker: ABF Sugar's 2025 margin collapse, Azucarera restructuring, Vivergo closure, Ubombo capacity and efficiency investment, and British Sugar decarbonisation projects.

The Human Review panel uses `data/engineering_sample_events.csv`, a five-record representative subset. The subset is intentionally not exhaustive. Its purpose is to demonstrate how prompt-chain based information extraction can produce reviewable, evidence-linked records that later relate to the analysis dashboard.

Semantic pipeline jobs now display multi-step prompt chains using expandable accordions. Each prompt step has a title, prompt text, input summary, expected output, and saved artifact. Non-LLM jobs still display implementation notes instead of artificial prompts.

The top Engineering toolbar includes a **Sample PDF** button next to Tutorial. It downloads the ABF Annual Report 2025 file bundled in `documents/04_abf-sugar/`.
