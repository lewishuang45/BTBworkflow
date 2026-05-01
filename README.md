# BTBworkflow

`BTBworkflow` is a local Python workflow for:

- reading a tabular CSV dataset
- cleaning and grouping records
- generating a structured analysis report with a configured text model API
- turning the report into a slide-style image prompt
- running a lightweight local dashboard to inspect workflow progress

This repository does not include live cloud credentials. You must manually provide your own API keys, endpoints, and deployment names before the workflow can run.

## Project structure

- `run_workflow.py` — main workflow entrypoint
- `webapp.py` — local dashboard backend
- `webui/` — dashboard frontend assets
- `assistant.py` — prompt/workflow editing assistant
- `workflow_prompts.json` — editable prompt configuration
- `workflow_labels.json` — dashboard labels and workflow definitions
- `dataset_schema.json` — schema mapping for reusable dataset preparation
- `analysis_template.json` — reusable analysis template metadata
- `sampleDATA.csv` — example input dataset
- `probe_image2.py` — minimal image generation connectivity probe
- `run_workflow.bat` / `run_workflow.ps1` — workflow launchers
- `run_image_generate.cmd` — image-only launcher
- `start_dashboard.cmd` — dashboard launcher

## Quick start

1. Create and activate a Python environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and manually fill in your own API settings.
4. Run the report stage:

   ```bash
   python run_workflow.py --stage report
   ```

5. Run the image stage:

   ```bash
   python run_workflow.py --stage image
   ```

6. Or start the dashboard:

   ```bash
   python webapp.py
   ```

## API Setup

The project is configuration-driven. Future users only need to fill in `.env`.

- `TEXT_MODEL_ENDPOINT` — text generation API base URL
- `TEXT_MODEL_API_KEY` — text generation API key
- `TEXT_MODEL_API_VERSION` — text API version
- `TEXT_MODEL_DEPLOYMENT` — text model deployment name
- `IMAGE_MODEL_ENDPOINT` — image generation API base URL
- `IMAGE_MODEL_API_KEY` — image generation API key
- `IMAGE_MODEL_API_VERSION` — image API version
- `IMAGE_MODEL_DEPLOYMENT` — image model deployment name

Once these values are set, no further code changes are required.

## Dataset Schema

The project now supports schema-driven preparation via `dataset_schema.json`.

- `input_file` — input data file name
- `id_column` — record identifier field
- `id_strategy` — currently supports `auto_increment`
- `ranking_column` — column used for ranking and segmentation
- `metric_columns` — columns required for analysis
- `drop_columns` — columns removed during cleaning
- `group_labels` — labels assigned to top / middle / bottom segments

## Analysis Template

The project also supports a lightweight template descriptor via `analysis_template.json`.

- `template_id` — unique template identifier
- `name` — user-facing template name
- `description` — what the template is for
- prompt key lists — which prompt blocks belong to report / outline / image generation

This is the next step toward a multi-template analytics product.

## Workspace Layout

You can now organize project inputs more like a reusable analytics workspace.

- Put reusable datasets in `datasets/`
- Put reusable template files in `templates/`
- The dashboard discovers these files automatically
- Dataset preparation now also outputs `preview_rows` and `chart_config` for downstream UI use

## Publish-safe notes

- Real credentials are not included.
- No live cloud resource names are required by default; you must configure your own `.env` values.
- Runtime caches, logs, and generated outputs are ignored by Git.
- The included CSV is treated as example project data; replace it if your real dataset is not public.
