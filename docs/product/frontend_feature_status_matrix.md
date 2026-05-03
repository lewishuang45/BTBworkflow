# Frontend Feature Status Matrix

This matrix is based on the current repository state in `C:\Capstone\workflow`.

## Audit basis

- The requested AI Ops Foundry backend paths are not present: `docs/`, `src/`, `mvp/`, `solution_packs/`, `tests/`, and `scripts/` were missing at audit time.
- The current repository is a different product: `README.md:1` describes `BTBworkflow`, a local Python analytics workflow with a lightweight dashboard.
- The visible implementation surface is limited to files such as `run_workflow.py:1`, `webapp.py:1`, `assistant.py:1`, `webui/index.html:1`, `workflow_prompts.json:1`, and `workflow_labels.json:1`.
- No Watsons demo outputs, AI Ops Foundry control plane, agent registry, solution packs, Azure Search RAG integration, or workflow runtime artifacts requested in the brief are available in this workspace.

## Status label definitions

- `Active`: backed by current code or output and safe to show as working.
- `Demo-ready`: backed by local fixture or output, but not production.
- `Limited`: partially implemented and needs careful wording.
- `Disabled`: should be visible but inactive in UI.
- `Planned`: intended but not implemented in this repo.
- `Design-only`: architectural concept only; no implementation found.

| Frontend Area | Feature | Backend Status | UI Label | Evidence Path | Can Show In Demo | Risk Of Overclaim | Required UI Wording | Notes |
|---|---|---|---|---|---|---|---|---|
| Agent Workspace | Interaction Agent | Design-only | Concept only | `README.md:1` | No | High | Not available in current repo | No agent workspace implementation found. |
| Agent Workspace | Ask / Run / Explain modes | Design-only | Concept only | `webapp.py:1` | No | High | Current app is a workflow dashboard, not an agent workspace | No multi-mode interaction surface. |
| Agent Workspace | Design mode | Design-only | Future concept | `README.md:1` | No | High | Not implemented in current repo | No design-agent flow. |
| Agent Workspace | Debug mode | Limited | Local workflow inspection only | `webapp.py:1` | Yes, carefully | Medium | Local workflow progress inspection only | Existing dashboard can inspect workflow progress, but not agent debugging. |
| Agent Workspace | Agent Dock | Design-only | Concept only | `README.md:1` | No | High | Not implemented in current repo | No agent registry UI. |
| Agent Workspace | Suggested actions | Design-only | Concept only | `assistant.py:1` | No | High | Prompt editing assistant exists, not proactive agent suggestions | Assistant edits prompts, not a workspace action engine. |
| Agent Workspace | Session memory / context summary | Design-only | Concept only | `assistant.py:1` | No | High | Not implemented in current repo | No session memory layer found. |
| Agent Workspace | Workflow execution strip | Limited | Workflow progress | `workflow_labels.json:1` | Yes, carefully | Low | Shows local workflow progress only | Can be adapted from existing dashboard progress view. |
| Solution Pack Studio | Solution pack registry | Planned | Future registry | `analysis_template.json:1` | No | High | Templates exist, solution packs do not | Template descriptors are not solution packs. |
| Solution Pack Studio | Retail Marketing Compliance pack | Planned | Not available | `templates/retail_compliance_template.json:1` | No | High | A retail compliance template exists, not the requested solution pack | No `solution_packs/retail_marketing_compliance/`. |
| Solution Pack Studio | Future packs | Planned | Future packs | `templates/:1` | No | Medium | Template-based future expansion only | Only lightweight template files found. |
| Solution Pack Studio | Workflow templates | Limited | Local templates | `analysis_template.json:1` | Yes, carefully | Medium | Local analysis templates, not agentic workflow templates | Existing template mechanism is analytics-oriented. |
| Solution Pack Studio | Rule sets | Planned | Not available | `templates/retail_compliance_template.json:1` | No | High | No rule-set runtime found | Template naming suggests compliance use case only. |
| Solution Pack Studio | Knowledge sources | Planned | Not available | `README.md:1` | No | High | No knowledge source management in current repo | No RAG or corpus handling found. |
| Solution Pack Studio | Approval policies | Planned | Not available | `README.md:1` | No | High | No approval policy backend found | No governance layer present. |
| Solution Pack Studio | Supported channels | Planned | Not available | `README.md:1` | No | High | No channel adapter system in current repo | No channel-neutral runtime. |
| Solution Pack Studio | Business Design Agent suggestions | Design-only | Concept only | `assistant.py:1` | No | High | Assistant edits prompts only | Not a business design agent. |
| Agent Registry | Interaction Agent | Design-only | Concept only | `README.md:1` | No | High | Not implemented in current repo | No agent registry found. |
| Agent Registry | Business / Solution Design Agent | Design-only | Concept only | `assistant.py:1` | No | High | Not implemented in current repo | No such agent defined. |
| Agent Registry | Code Debug Agent | Limited | Local prompt/workflow assistant | `assistant.py:1` | Yes, carefully | Medium | Assistant can edit workflow prompts and config locally | Not a code debugging runtime. |
| Agent Registry | Retail Compliance Agent | Planned | Not available | `templates/retail_compliance_template.json:1` | No | High | No specialist agent backend found | Only a template hint exists. |
| Agent Registry | Advertising Visual Agent | Planned | Not available | `probe_image2.py:1` | No | High | Image connectivity probe only | No visual specialist workflow found. |
| Agent Registry | Legal Expert Agent | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No legal reasoning backend. |
| Agent Registry | RAG / Knowledge Curator | Planned | Not available | `README.md:1` | No | High | No RAG backend found | No Azure Search references found. |
| Agent Registry | Policy Guard | Planned | Not available | `README.md:1` | No | High | No policy layer found | No approval or guardrail module. |
| Agent Registry | Audit / Receipts Agent | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No receipts or audit runtime. |
| Agent Registry | Future specialists | Planned | Future specialists | `PRODUCT_ROADMAP.md:1` | No | Medium | Future expansion only | Can be listed as future roadmap if clearly marked. |
| Workflow Studio | Workflow template viewing | Limited | Local workflow config | `workflow_labels.json:1` | Yes, carefully | Medium | Shows local step labels/config, not full workflow templates | Existing config is shallow. |
| Workflow Studio | Visual workflow graph | Disabled | Not available | `webui/index.html:1` | No | High | Not implemented in current repo | No graph visualization found. |
| Workflow Studio | Step configuration | Limited | Config editing | `assistant.py:1` | Yes, carefully | Medium | Prompt/config editing only | Can expose prompt and label editing. |
| Workflow Studio | Save/publish template | Disabled | Local save only | `assistant.py:1` | No | Medium | Local file save only; no publish workflow | No registry or deployment flow. |
| Workflow Studio | Validate template | Disabled | Not available | `README.md:1` | No | High | No template validator found | No workflow-template schema validation found. |
| Workflow Studio | Code Debug Agent explain step | Limited | Local explainability of workflow config | `assistant.py:1` | Yes, carefully | Medium | Explain current local workflow config only | No agent-generated patch reasoning. |
| Workflow Studio | Code Debug Agent generate patch plan | Disabled | Not available | `assistant.py:1` | No | High | Not implemented in current repo | No patch-plan feature found. |
| Workflow Run Detail | Watsons 5-asset workflow | Planned | Not available | `README.md:1` | No | High | Watsons demo artifacts are not present in this repo | Requested evaluation path missing. |
| Workflow Run Detail | Asset list | Planned | Not available | `README.md:1` | No | High | No asset-review workflow in current repo | No campaign review outputs. |
| Workflow Run Detail | Annotated SVG viewer | Planned | Not available | `probe_image2.py:1` | No | High | No annotated SVG artifacts found | Image probe is unrelated. |
| Workflow Run Detail | Issue regions | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No issue region outputs. |
| Workflow Run Detail | Rule citations | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No rule-grounding outputs. |
| Workflow Run Detail | Human review packet | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No review packet artifacts. |
| Workflow Run Detail | Warning email payload | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No warning payload artifacts. |
| Workflow Run Detail | Receipts / audit | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No audit receipt outputs. |
| Workflow Run Detail | Raw JSON/debug view | Demo-ready | Local workflow artifacts | `webapp.py:1` | Yes | Low | Local JSON artifact inspection only | Current product already renders/report JSON-like outputs. |
| Knowledge & RAG | Azure Search status | Planned | Not connected | `README.md:1` | No | High | No Azure Search integration in current repo | Search terms returned no Azure Search evidence. |
| Knowledge & RAG | Live index | Planned | Not connected | `README.md:1` | No | High | Not implemented in current repo | No live index. |
| Knowledge & RAG | Document count | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No corpus metadata. |
| Knowledge & RAG | Retrieval validation | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No retrieval validation reports. |
| Knowledge & RAG | Citation explorer | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No citations system. |
| Knowledge & RAG | Retrieval explorer | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No retrieval tooling. |
| Knowledge & RAG | Production corpus separation | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No corpus separation model. |
| Knowledge & RAG | Source provenance | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No provenance layer. |
| Knowledge & RAG | RAG context used in specialist eval | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No specialist eval system. |
| Human Review | Review queue | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No review queue. |
| Human Review | Human review packet | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | Missing packet outputs. |
| Human Review | Annotated asset | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | Missing asset annotations. |
| Human Review | Required actions | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No task/action engine. |
| Human Review | Approve/reject/request evidence | Disabled | Future controls | `webapp.py:1` | No | High | Controls should remain disabled until writeback exists | No approval writeback. |
| Human Review | Legal escalation | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No escalation path. |
| Human Review | Approval writeback | Disabled | Not connected | `README.md:1` | No | High | No backend writeback implemented | Keep disabled in any future UI stub. |
| Receipts & Audit | Local receipts | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No receipt files found. |
| Receipts & Audit | Audit logs | Limited | Local workflow state only | `webapp.py:1` | Yes, carefully | Medium | Local workflow state is not a formal audit log | Existing state tracking is operational only. |
| Receipts & Audit | workflow_run.json | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | Missing file. |
| Receipts & Audit | task_status.json | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | Missing file. |
| Receipts & Audit | Specialist receipts | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No specialist runtime. |
| Receipts & Audit | RAG retrieval receipts | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No RAG backend. |
| Receipts & Audit | Production audit retention | Design-only | Concept only | `PUBLIC_RELEASE_CHECKLIST.md:1` | No | High | No production audit retention in current repo | No retention controls found. |
| Channels & Adapters | Email local fixture | Disabled | Not available | `README.md:1` | No | High | No email fixture in current repo | No warning email payload artifact. |
| Channels & Adapters | Real Outlook/Graph | Planned | Future integration | `README.md:1` | No | High | Not implemented in current repo | Safe to label future only. |
| Channels & Adapters | Copilot adapter | Planned | Future adapter | `NODE_PRODUCT_ARCHITECTURE.md:1` | No | High | Future-compatible direction only | No adapter implementation found. |
| Channels & Adapters | Teams adapter | Planned | Future adapter | `NODE_PRODUCT_ARCHITECTURE.md:1` | No | High | Not implemented in current repo | No Teams integration found. |
| Channels & Adapters | SharePoint adapter | Planned | Future adapter | `NODE_PRODUCT_ARCHITECTURE.md:1` | No | High | Not implemented in current repo | No SharePoint integration found. |
| Channels & Adapters | API webhook | Planned | Future adapter | `NODE_PRODUCT_PLAN.md:1` | No | Medium | Not implemented in current repo | Only roadmap-level direction. |
| Channels & Adapters | Manual upload | Active | Local file input | `README.md:16` | Yes | Low | Local dataset file input is supported | Current product supports local datasets. |
| Channels & Adapters | MCP action adapter | Planned | Future adapter | `NODE_PRODUCT_ARCHITECTURE.md:1` | No | High | Not implemented in current repo | No MCP adapter implementation. |
| Build & Debug | Runtime map | Limited | Local workflow map | `workflow_labels.json:1` | Yes, carefully | Low | Shows local workflow stages only | Not an agentic runtime map. |
| Build & Debug | Code Debug Agent console | Disabled | Not available | `assistant.py:1` | No | High | Assistant exists, console does not | No debug console feature. |
| Build & Debug | Recent eval results | Disabled | Not available | `README.md:1` | No | High | No eval framework in current repo | Requested eval files absent. |
| Build & Debug | Patch plan | Disabled | Not available | `assistant.py:1` | No | High | Not implemented in current repo | No patch planning feature. |
| Build & Debug | Test runner | Disabled | Not available | `README.md:1` | No | High | No tests present in current repo | `tests/` missing. |
| Build & Debug | Apply patch | Disabled | Not available | `README.md:1` | No | High | Not a product feature in current repo | Development tooling only. |
| Build & Debug | Create PR | Disabled | Not available | `README.md:1` | No | High | Not implemented in current repo | No SCM integration. |
| Governance / Policy / Approvals | Approval gate | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No policy engine. |
| Governance / Policy / Approvals | No-final-legal-judgment guardrail | Planned | Future guardrail | `README.md:1` | No | High | Not implemented in current repo | Can be documented as UI copy only later. |
| Governance / Policy / Approvals | Synthetic/client-demo guardrail | Planned | Future guardrail | `PUBLIC_RELEASE_CHECKLIST.md:1` | No | Medium | Only publish-safe notes exist today | No runtime enforcement. |
| Governance / Policy / Approvals | Production authorization | Planned | Not available | `PUBLIC_RELEASE_CHECKLIST.md:1` | No | High | Not implemented in current repo | No authz model found. |
| Governance / Policy / Approvals | Policy rules | Planned | Not available | `README.md:1` | No | High | Not implemented in current repo | No policy rules store. |
| Governance / Policy / Approvals | Data classification | Planned | Not available | `dataset_schema.json:1` | No | Medium | Dataset schema is not a data classification system | Avoid overclaim. |
| Governance / Policy / Approvals | Access control | Planned | Not available | `webapp.py:1` | No | High | Not implemented in current repo | Local dashboard only. |

## Safe demo scope in this repository

The only frontend-facing areas that are reasonably supportable from current evidence are:

- local workflow progress/state visualization
- local dataset/template selection
- local prompt/config editing
- local JSON/report inspection

These are not AI Ops Foundry platform capabilities and should not be presented as such.

