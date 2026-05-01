# BTBworkflow Node.js Product Plan

## Phase 0 — Decision and Freeze

### Objective
Freeze the Python MVP as a reference implementation.

### Deliverables
- feature inventory
- domain inventory
- migration map

## Phase 1 — Node.js Foundation

### Objective
Set up the production monorepo and infrastructure baseline.

### Tasks
- initialize monorepo
- set up `Next.js` frontend
- set up `Fastify` or API app
- set up `Prisma` + PostgreSQL
- set up shared packages
- set up environment config and secrets handling

### Exit Criteria
- local web app boots
- API boots
- DB connection works
- auth placeholder works

## Phase 2 — Core Product Objects

### Objective
Build the real product data model.

### Tasks
- implement users / workspaces / roles
- implement datasets
- implement templates
- implement runs
- implement artifacts

### Exit Criteria
- dataset upload stored in DB + storage
- templates listed from DB or package layer
- runs are created and tracked

## Phase 3 — Workflow Execution Engine

### Objective
Rebuild the current Python workflow capability in Node.js services.

### Tasks
- dataset preparation service
- schema validation service
- AI analysis service
- chart config generation
- export service
- worker queue setup

### Exit Criteria
- one full run can execute asynchronously
- run logs and artifacts persist
- results render in frontend

## Phase 4 — Product UX Completion

### Objective
Move from engineering console to real product UI.

### Tasks
- dataset upload UX
- field mapping form
- template cards and template details
- structured findings view
- chart rendering view
- artifact download page

### Exit Criteria
- non-technical user can complete one run end-to-end

## Phase 5 — Production Launch Readiness

### Objective
Prepare for deployment and operation.

### Tasks
- logging and monitoring
- background job retries
- rate limiting
- audit logs
- staging environment
- backup and rollback plan
- load and cost testing

### Exit Criteria
- staging is stable
- failure handling is documented
- release checklist is complete

