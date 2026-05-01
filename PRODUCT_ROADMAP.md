# BTBworkflow Product Roadmap

## Vision

Turn `BTBworkflow` from a single-dataset workflow into a reusable AI-assisted analytics workbench.

## MVP Direction

The first productized version should support:

- arbitrary tabular input files
- configurable schema mapping
- reusable analysis templates
- configurable segmentation logic
- structured report output
- dashboard-driven runs

## Immediate Refactor Priorities

### 1. Schema-driven dataset preparation
- Remove hard-coded source column assumptions.
- Add a local schema file that defines:
  - id column strategy
  - ranking column
  - included metric columns
  - columns to drop
  - grouping labels

### 2. Template-driven analysis
- Separate dataset preparation from prompt semantics.
- Allow future templates like:
  - leaderboard comparison
  - time-series summary
  - cohort comparison
  - A/B result narrative

### 3. Multi-task structure
- Each run should eventually become a task with:
  - input source
  - schema config
  - analysis template
  - outputs

## Recommended Next Milestones

1. Add schema config support
2. Add alternate input file selection
3. Add template selector in the dashboard
4. Add chart config output for frontend rendering
5. Add report export targets

## Productization Status

- Input layer: implemented with local uploads, schema config, and preview
- Template layer: implemented with starter templates and template switching
- Insight layer: partially implemented with structured starter insights and AI report generation
- Delivery layer: implemented with JSON, image preview, chart preview, and HTML export
- Workspace layer: implemented with datasets and templates directories plus dashboard controls
