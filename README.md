# BTBworkflow

`BTBworkflow` is a local Python workflow for:

- reading a tabular CSV dataset
- cleaning and grouping records
- generating a structured analysis report with Azure OpenAI text models
- turning the report into a slide-style image prompt
- running a lightweight local dashboard to inspect workflow progress

## Project structure

- `run_workflow.py` — main workflow entrypoint
- `webapp.py` — local dashboard backend
- `webui/` — dashboard frontend assets
- `assistant.py` — prompt/workflow editing assistant
- `workflow_prompts.json` — editable prompt configuration
- `workflow_labels.json` — dashboard labels and workflow definitions
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

3. Copy `.env.example` to `.env` and fill in your Azure OpenAI settings.
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

## Publish-safe notes

- Real credentials are not included.
- Runtime caches, logs, and generated outputs are ignored by Git.
- The included CSV is treated as example project data; replace it if your real dataset is not public.

## Recommended first commit

After creating a new GitHub repository named `BTBworkflow`, initialize Git locally and push:

```bash
git init
git add .
git commit -m "Initial public release"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

