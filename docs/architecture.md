# Architecture

BTBworkflow is a Python MVP for an AI-assisted analyst workflow. It is intentionally small: local files, one CLI entrypoint, and a lightweight dashboard. The repo is meant to show the product loop clearly before any SaaS infrastructure is added.

## Python MVP Shape

- `run_workflow.py` owns the workflow pipeline.
- `workflow_labels.json` defines the ordered steps and the action attached to each step.
- `webapp.py` serves a local dashboard and exposes small JSON endpoints for running stages, editing prompts, and inspecting outputs.
- `webui/` contains static dashboard assets.
- Runtime outputs such as `final_output.json`, `chart_config.json`, and `workflow_state.json` are generated locally and ignored by Git.

## Configuration-Driven Dataset Schema

`dataset_schema.json` describes how a structured dataset should be prepared:

- input file
- record ID column
- ranking column
- metric columns
- columns to drop
- group labels

The pipeline uses this schema to load the CSV, add or preserve IDs, remove configured columns, rank records, split groups, and produce chart-ready summaries.

## Template-Driven Analysis

`analysis_template.json` selects prompt blocks and expected fields for a specific analysis type. The current MVP keeps templates lightweight so new use cases can be added without changing the core workflow.

Templates define:

- report prompt keys
- outline prompt keys
- image prompt keys
- system prompt guidance
- optional expected dataset fields

## Model Provider Configuration

Live mode reads provider settings from environment variables or `.env`:

- text model endpoint, key, API version, and deployment
- image model endpoint, key, API version, and deployment

The current implementation uses Azure OpenAI-style request shapes. A production version should wrap these calls behind provider-neutral adapters so OpenAI, Azure, Anthropic, Gemini, or local models can be configured without changing workflow logic.

## Mock Vs Live Mode

Mock mode is the public-demo path. It:

- uses the sample dataset,
- generates deterministic report JSON,
- writes deterministic chart config,
- creates a placeholder presentation HTML artifact,
- updates workflow state,
- does not call external APIs,
- does not require `.env`.

Live mode follows the same workflow stages but sends text and image actions to configured model APIs.

## Dashboard Role

The dashboard is a local inspection surface, not a production app. It helps reviewers see:

- workflow state,
- prompt and template configuration,
- dataset/schema settings,
- generated report JSON,
- chart config,
- presentation artifacts.

This keeps the MVP useful for demos while avoiding premature SaaS complexity.

## Planned Node.js Production Migration

The production direction is a Node.js application with:

- authenticated users,
- project workspaces,
- uploaded datasets,
- reusable schema and template libraries,
- background workflow jobs,
- durable storage,
- provider-neutral model adapters,
- shareable report and slide artifacts.

The Python MVP should remain the reference implementation for the core workflow until the product shape is proven.
