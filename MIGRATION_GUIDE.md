# BTBworkflow Migration Guide

## Purpose
This project provides a local workflow for:
- reading `sampleDATA.csv`
- preparing grouped analysis data
- generating a JSON analysis report with Azure OpenAI text models
- running a local dashboard for workflow control and progress tracking
- generating a final slide-style image with Azure `image2`

## Main Entry Points
- Full workflow: `run_workflow.bat`
- Image generation only: `run_image_generate.cmd`
- Dashboard: `start_dashboard.cmd`
- Main Python workflow: `run_workflow.py`
- Dashboard backend: `webapp.py`

## Environment Setup
Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_TEXT_DEPLOYMENT`
- `AZURE_OPENAI_IMAGE_ENDPOINT`
- `AZURE_OPENAI_IMAGE_API_KEY`
- `AZURE_OPENAI_IMAGE_API_VERSION`
- `AZURE_OPENAI_IMAGE_DEPLOYMENT`

## Recommended Local Run Paths
### Run dashboard
```bash
start_dashboard.cmd
```

### Run report only
```bash
python run_workflow.py --stage report
```

### Run image generation only
```bash
run_image_generate.cmd
```

### Run image probe only
```bash
python probe_image2.py
```

## Publish Notes
- Keep `.env` local only.
- Do not commit generated outputs or runtime cache files.
- Replace `sampleDATA.csv` if your actual data is not public.
