# Frontend Implementation Plan

## Recommendation

Do **not** build the AI Ops Foundry frontend yet from this repository state.

The current workspace does not contain the backend artifacts, demo outputs, solution packs, or evaluation evidence named in the brief. Building now would force the frontend to invent data contracts and would create a high risk of overclaim.

## Rationale for Streamlit

When the correct backend artifacts are available, a local `Streamlit` frontend is still a good choice for the first demo because it:

- is fast to iterate locally
- reads local files easily
- supports a multi-page demo shell
- is well suited to evidence panels, JSON views, and operator-style workflows
- lowers ceremony compared with a full React implementation

## Preconditions before frontend implementation

Frontend implementation should begin only after these inputs exist in-repo:

- solution pack definitions
- workflow templates
- Watsons 5-asset run outputs
- annotated asset artifacts
- RAG validation and ingestion reports
- receipts and audit artifacts
- explicit disabled/future capability registry

## Pages to build first

Only after the correct backend exists:

- `Agent Workspace`
- `Solution Pack Studio`
- `Workflow Run Detail`
- `Agent Registry`
- `Knowledge & RAG`
- `Build & Debug`

## Pages to keep simpler or status-only

- `Channels & Adapters`
- `Governance / Policy / Audit`
- `Admin / Settings`

## Components

- sidebar navigation
- agent dock
- interaction canvas
- workflow timeline
- annotated SVG viewer
- citation cards
- human review packet preview
- warning email preview
- runtime status cards
- disabled feature tags

## File readers

The future frontend should read from a small file-loader layer that:

- checks whether each declared source path exists
- returns structured `present / missing / stale` state
- parses JSON, JSONL, YAML, Markdown, SVG, and image references
- emits explicit fallback models for disabled features

## Error and fallback handling

- Missing required file: block the dependent panel and show a specific missing-path warning.
- Missing optional file: hide the panel and render a disabled/future tag.
- Invalid JSON or YAML: render a parse error card instead of best-guess data.
- Empty directory of annotations: hide the annotated viewer.
- Report-only evidence without machine-readable payload: render markdown summary cards, not interactive controls.

## Proposed demo launch command

```bash
streamlit run demo_ui/app.py
```

Do not create `demo_ui/app.py` until the correct backend inputs are available.

## Boundaries

- no real email sending
- no real Copilot, Graph, or Teams integration
- no production approval writeback
- no full `.ai` parser
- no final legal judgment
- no production-readiness claim

## Suggested build phases

### Phase UI-1: data loaders and layout shell

- implement shared file readers
- implement page routing and global disabled-feature tags
- wire page shells to the data contract

### Phase UI-2: Agent Workspace and Workflow Run Detail

- add workspace shell
- add run detail paneling
- add raw JSON and evidence tabs

### Phase UI-3: Solution Pack Studio and Agent Registry

- add solution pack blueprint views
- add registry groupings and agent detail panels

### Phase UI-4: Knowledge & RAG and Build & Debug

- add retrieval explorer
- add citation evidence views
- add eval and validation summaries

### Phase UI-5: final demo polish

- improve wording consistency
- improve disabled-state styling
- tune demo story flow

## Current go/no-go assessment

Current state is **no-go** for implementation of the requested platform frontend from this repo alone.

Safe next step is to first obtain or restore the AI Ops Foundry backend/docs branch, then rerun this audit against the correct codebase.

