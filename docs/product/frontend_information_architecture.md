# Frontend Information Architecture

## Positioning

The requested target product is an **AI Ops Foundry Agent Workspace**, not a Watsons-only KPI dashboard.

However, the current repository does **not** contain the AI Ops Foundry backend, solution packs, Watsons demo outputs, or platform runtime artifacts described in the brief. Because of that, this information architecture is a **proposed future IA** for the intended platform, with clear activation boundaries tied to missing backend evidence.

## Current audit conclusion

- Safe to design the IA conceptually.
- Not safe to present most pages as active from this repository.
- If frontend work proceeds from this repo alone, most platform pages must be visibly future-labeled or disabled.

## Global navigation

- `Agent Workspace`
- `Work Sessions`
- `Solution Packs`
- `Agent Registry`
- `Workflow Studio`
- `Workflow Run Detail`
- `Knowledge & RAG`
- `Human Review`
- `Receipts & Audit`
- `Channels & Adapters`
- `Build & Debug`
- `Governance`
- `Admin / Settings`

## Page-by-page purpose

### 1. Agent Workspace

- Primary operating surface for human-plus-agent collaboration.
- Anchors the platform around task execution, explanation, design, and debug flows.
- In current repo state: keep as `future platform shell` only.

### 2. Work Sessions

- Lists active and prior workspace sessions, context summaries, and run history.
- In current repo state: disabled.

### 3. Solution Packs / Solution Pack Studio

- Shows packaged industry or domain solutions, their workflow templates, rule sets, knowledge sources, and governance envelope.
- In current repo state: only a loose analogy to local templates exists.

### 4. Agent Registry

- Shows available core, specialist, and governance agents.
- In current repo state: disabled.

### 5. Workflow Studio

- Visualizes workflow templates and configures steps.
- In current repo state: only local workflow label/config editing is partially supportable.

### 6. Workflow Run Detail

- Displays artifacts, evidence, decisions, and receipts for a run.
- In current repo state: only generic local JSON/report detail is supportable.

### 7. Knowledge & RAG

- Surfaces knowledge indexes, retrieval inspection, provenance, and validation.
- In current repo state: disabled.

### 8. Human Review

- Queues items requiring human action and binds review decisions to evidence.
- In current repo state: disabled.

### 9. Receipts & Audit

- Consolidates execution receipts, evidence chain, and audit events.
- In current repo state: only light local workflow state inspection is supportable.

### 10. Channels & Adapters

- Describes ingress/egress adapters such as manual upload, email, API, Teams, or Copilot.
- In current repo state: only manual upload is real.

### 11. Build & Debug

- Gives builders insight into runtime status, evaluations, and debug tooling.
- In current repo state: only local workflow map/config visibility is supportable.

### 12. Governance / Policies / Approvals

- Exposes rules, approval controls, and operating boundaries.
- In current repo state: disabled.

### 13. Admin / Settings

- Holds environment configuration, feature flags, and operator settings.
- In current repo state: could expose local config only, but should not imply enterprise administration.

## Detailed page layouts

### A. Agent Workspace

- Left: context and task panel.
- Center: interaction canvas with `Ask`, `Run`, `Explain`, `Design`, and `Debug` tabs.
- Right: Agent Dock.
- Bottom: execution strip and active workflow summary.

**Activation guidance**

- Active now: none.
- Disabled/future: all tabs except a possible `Local Debug` placeholder.
- Required badge: `Future platform surface — backend not available in current repo`.

### B. Solution Pack Studio

- Left: pack list.
- Center: solution pack blueprint.
- Right: Business Design Agent suggestions and actions.
- Disabled buttons for pack creation if not implemented.

**Activation guidance**

- Active now: none.
- Limited substitute: map current local templates into a temporary `Templates` card, not a `Solution Packs` claim.

### C. Workflow Studio

- Left: workflow template tree.
- Center: visual workflow graph.
- Right: step configuration and Code Debug Agent helper.
- Save/publish disabled unless implemented.

**Activation guidance**

- Active now: local workflow label/config inspection only.
- Disabled/future: graph, publish, validator, debug agent helper.

### D. Workflow Run Detail

- Left: run context and timeline.
- Center: artifacts and annotated asset viewer.
- Right: decision, evidence, top RAG citations, required action.
- Bottom tabs: packet, warning email, receipts, raw JSON.

**Activation guidance**

- Active now: raw JSON/debug view only, based on local workflow/report outputs.
- Disabled/future: annotated asset viewer, citations, packet, warning email, receipts.

### E. Agent Registry

- Group agents into `Core Platform Agents`, `Solution Expansion Agents`, `Specialist Agents`, `Governance Agents`, and `Runtime Support Agents`.
- Include detail panel per agent.

**Activation guidance**

- Active now: none.
- If shown, every agent card except a local assistant/config editor stub must be marked `Future`.

### F. Build & Debug

- Runtime map.
- Code Debug Agent console.
- Patch plan panel.
- Tests and validation status.
- Apply patch / create PR disabled unless implemented.

**Activation guidance**

- Active now: runtime map analogue from local workflow stages.
- Disabled/future: agent console, patch plan, test runner, apply patch, create PR.

### G. Knowledge & RAG

- Index list.
- Retrieval explorer.
- Citation map.
- Retrieval validation summary.

**Activation guidance**

- Active now: none.
- Entire page should be disabled/future until real RAG assets exist.

### H. Channels & Adapters

- Adapter list.
- Adapter contract.
- Future integration path.
- Copilot clearly marked future-compatible / not connected.

**Activation guidance**

- Active now: `Manual Upload` only.
- Disabled/future: Email, Outlook/Graph, Teams, SharePoint, API webhook, Copilot, MCP.

### I. Governance / Policy / Audit

- Approval gates.
- Legal boundary controls.
- Receipts.
- Audit events.
- Guardrails.

**Activation guidance**

- Active now: none.
- If shown, use read-only policy placeholders and explicit disabled tags.

## Core layout principles

- Agent-workspace first.
- Watsons should appear as a solution pack and workflow run, not the whole product.
- RAG and citations should appear as explainability evidence, not vanity metrics.
- Channels should be framed as adapters around the runtime, not the system core.
- Future capabilities must be visibly marked `Disabled`, `Planned`, or `Concept`.

## Recommended demo flow

Given current repo state, the safe demo flow is **not** the requested platform flow. The safe flow is:

- select a local dataset
- inspect or edit local template/config
- run the local workflow
- inspect generated report/output state in the local dashboard

For the intended AI Ops Foundry frontend, the recommended future demo flow would be:

- open `Agent Workspace`
- select `Retail Marketing Compliance` solution pack
- inspect workflow template
- run the Watsons 5-asset review
- inspect `Workflow Run Detail`
- inspect `Knowledge & RAG` evidence
- inspect `Receipts & Audit`

That future flow should not be built as active until the corresponding backend exists in-repo.

