# BTBworkflow Node.js Product Architecture

## Goal

Rebuild `BTBworkflow` as a production-oriented Node.js product while preserving the current MVP product concepts:

- dataset ingestion
- schema-driven preparation
- template-driven analysis
- AI-generated insights
- chart and report delivery
- exportable artifacts

## Recommended Stack

### Frontend
- `Next.js` with `TypeScript`
- App Router
- component-driven dashboard UI
- `ECharts` for chart rendering

### Backend API
- `Fastify` or `Next.js` route handlers for light APIs in early stages
- move to dedicated service modules under `apps/api` for production scale

### Database
- `PostgreSQL`
- `Prisma` ORM

### Queue / Jobs
- `BullMQ` with Redis

### Storage
- local dev: filesystem
- production: Azure Blob Storage or S3-compatible storage

### Auth
- `NextAuth` or external auth provider
- workspace-based RBAC

## Product Domains

### 1. Identity
- users
- sessions
- workspace membership
- roles

### 2. Workspace
- workspace settings
- provider configuration
- active template defaults

### 3. Dataset
- uploaded files
- dataset versions
- schema mapping
- validation status

### 4. Template
- template metadata
- expected fields
- prompt strategy
- chart preferences

### 5. Run
- queued / running / completed / failed
- execution logs
- selected dataset and template

### 6. Artifact
- report JSON
- chart config
- slide image
- HTML export

## Suggested Monorepo Structure

```text
btbworkflow/
  apps/
    web/
      app/
      components/
      lib/
      public/
    api/
      src/
        routes/
        modules/
        services/
        jobs/
        utils/
  packages/
    config/
    db/
    schemas/
    templates/
    ui/
    analytics-core/
  prisma/
    schema.prisma
  docs/
  infra/
    docker/
    deploy/
```

## Core Services

### Dataset Service
- upload dataset
- parse CSV/XLSX
- infer columns
- validate against schema

### Schema Service
- save mappings
- validate required fields
- compute preview rows

### Template Service
- list templates
- activate template
- validate template-to-schema fit

### Analysis Service
- generate prepared dataset summary
- build prompt payloads
- call AI provider
- normalize output into findings / risks / recommendations

### Artifact Service
- save report JSON
- save chart config
- save image
- export HTML/PDF

### Run Service
- create run
- queue job
- update run status
- persist logs and artifacts

## Data Flow

1. user uploads dataset
2. dataset is parsed and profiled
3. user maps fields / selects template
4. system validates schema-template compatibility
5. user starts run
6. background worker executes preparation + AI analysis + artifact generation
7. frontend subscribes to run status and renders results

## MVP-to-Production Migration Principle

Do not migrate the current Python file structure line-by-line.

Instead:
- keep the current repo as product logic reference
- reimplement stable concepts in a Node.js service architecture
- migrate by domain, not by file name

