# BTBworkflow Python-to-Node Migration Map

## Purpose

Map the current Python MVP concepts into the future Node.js production architecture.

## Current to Future Mapping

### `run_workflow.py`
Current role:
- workflow orchestration
- dataset preparation
- provider calls
- artifact writing

Future split:
- `packages/analytics-core`
- `apps/api/src/modules/analysis`
- `apps/api/src/jobs`
- `apps/api/src/modules/artifacts`

### `webapp.py`
Current role:
- local HTTP server
- dashboard API
- state exposure

Future split:
- `apps/web`
- `apps/api/src/routes`
- `apps/api/src/modules/runs`

### `dataset_schema.json`
Current role:
- local file-based schema config

Future destination:
- database-backed dataset schema mappings

### `analysis_template.json` and `templates/*.json`
Current role:
- template metadata and prompt grouping

Future destination:
- template catalog service
- DB-backed template records or versioned packaged templates

### `workflow_prompts.json`
Current role:
- local prompt snippets

Future destination:
- prompt registry or template-bound prompt store

### `final_output.json`, `report_output.html`, images
Current role:
- local generated artifacts

Future destination:
- artifact storage + artifact metadata table

## Migration Recommendation

Do the migration by capability slices:

1. dataset ingestion
2. schema mapping
3. template catalog
4. run orchestration
5. artifact delivery

Do not migrate by copying file names or trying to preserve the same runtime shape.

