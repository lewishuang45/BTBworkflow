import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
PROMPTS_FILE = ROOT / "workflow_prompts.json"
LABELS_FILE = ROOT / "workflow_labels.json"
HISTORY_FILE = ROOT / "workflow_assistant_history.json"

ALLOWED_CHANGE_TYPES = {
    "replace_prompt",
    "append_prompt_instruction",
    "add_prompt",
    "remove_prompt",
    "add_step",
    "remove_step",
    "update_step",
    "update_step_action",
    "reorder_steps",
    "add_substep",
    "remove_substep",
    "update_substep",
}

STEP_CHANGE_TYPES = {
    "add_step", "remove_step", "update_step", "update_step_action",
    "reorder_steps", "add_substep", "remove_substep", "update_substep",
}


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return fallback


def _build_system_prompt() -> str:
    return (
        "You are a workflow editor for a local data-analysis pipeline. The pipeline is "
        "DATA-DRIVEN: every step in workflow_labels.json carries an 'action' field that the "
        "runner dispatches by type. Adding a new step with a valid action makes that step "
        "ACTUALLY execute. Adding a new prompt key is meaningful only if some step.action "
        "references it.\n\n"
        "Inputs you receive: the user's natural-language request, the current "
        "workflow_prompts.json (prompt keys), and the current workflow_labels.json (steps with "
        "actions). Translate the request into a precise list of structured changes.\n\n"
        "Output STRICT JSON only with this shape:\n"
        '{"summary": "<one-line plain-English summary>", "notes": "<optional caveats>", '
        '"changes": [<change>, ...]}\n\n'
        "=== CHANGE TYPES ===\n"
        "Prompt edits:\n"
        "- replace_prompt: {type, target: <prompt_key>, value: string}\n"
        "- append_prompt_instruction: {type, target, value}\n"
        "- add_prompt: {type, key, value}                 # new prompt key, must not collide\n"
        "- remove_prompt: {type, key}                     # rejected if any step.action references it\n"
        "Step edits:\n"
        "- add_step: {type, id, title, detail, after?: <step_id>|'start'|'end', "
        "stages?: [<stage>, ...], action: <action>, substeps?: [{id, label}, ...]}\n"
        "- remove_step: {type, id}\n"
        "- update_step: {type, id, title?, detail?, stages?}\n"
        "- update_step_action: {type, id, action: <action>}   # replace step.action wholesale\n"
        "- reorder_steps: {type, order: [step_id, ...]}\n"
        "- add_substep / remove_substep / update_substep: as before\n\n"
        "=== ACTION SCHEMA (the 'action' field) ===\n"
        "An action is {\"type\": <one of below>, ...fields}. Fields per type:\n"
        "- load_env: {type:'load_env'}                        # load Azure creds into ctx\n"
        "- prepare_dataset: {type:'prepare_dataset', output_to:'data_summary'}\n"
        "- llm_text: {type:'llm_text', system: string, user_parts: [<part>, ...], "
        "temperature?: number, response_format?: 'json_object'|'text', output_to: <ctx_key>, "
        "save_to?: {file: string, wrap?: <template>}}\n"
        "- build_image_boundary: {type:'build_image_boundary', input_from:'outline_report', "
        "fallback_file?: 'final_output.json', output_to:'image_soft_boundary', "
        "output_file:'image_soft_boundary.json'}\n"
        "- build_image_prompts: {type:'build_image_prompts', input_from:'outline_report', "
        "fallback_file?: 'final_output.json', output_to:'image_prompts'}\n"
        "- llm_image: {type:'llm_image', input_from:'image_prompts', output_file: string, "
        "patch_after?: {file, patch: <template>}}\n"
        "- save_json: {type:'save_json', file: string, wrap?: <template>, from_ctx?: <ctx_key>}\n"
        "- patch_json: {type:'patch_json', file: string, patch: <template>}\n\n"
        "=== user_parts (composes the LLM user message by concatenation) ===\n"
        "Each part is exactly one of:\n"
        "- {text: string}                literal text\n"
        "- {prompt: <prompt_key>}        substitutes prompt content\n"
        "- {ctx: <ctx_key>, format?: 'json'|'text'}    substitutes ctx slot value\n"
        "- {env: <ENV_VAR>}              substitutes environment variable\n\n"
        "=== template (used in save_to.wrap and patch_after.patch) ===\n"
        "A JSON object/array; these special leaf forms are resolved at runtime:\n"
        "- {\"$output\": true}           replaced by this step's output\n"
        "- {\"$ctx\": <ctx_key>}         replaced by ctx slot value\n"
        "- {\"$env\": <ENV_VAR>}         replaced by env var\n"
        "Anything else is a literal.\n\n"
        "=== ctx slots produced by the existing pipeline ===\n"
        "data_summary, analysis_report, outline_report, image_prompts. New steps may read these "
        "or write their own. Avoid leading underscore (reserved).\n\n"
        "=== Rules ===\n"
        "1. Smallest change set that satisfies the request.\n"
        "2. New step ids and prompt keys: lowercase snake_case, unique.\n"
        "3. When user says 'add a step that uses prompt_X', generate BOTH the prompt (if it "
        "doesn't exist yet, via add_prompt) AND a step with action.type='llm_text' referencing it.\n"
        "4. New llm_text steps should set response_format='json_object' unless user wants free text.\n"
        "5. Default new steps to stages: ['all', 'report'] for analysis-style, ['all', 'image'] "
        "for image-style; pick what fits.\n"
        "6. Don't reference ctx slots that aren't produced by some prior step.\n"
        "7. If ambiguous or impossible, return empty changes and explain in 'notes'.\n"
        "8. Output strict JSON only — no markdown fences, no commentary."
    )


def request_suggestion(message: str, prompts: dict, labels: dict) -> dict:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    deployment = os.getenv("AZURE_OPENAI_TEXT_DEPLOYMENT", "gpt54-workflow")
    if not endpoint or not api_key:
        raise RuntimeError("Azure OpenAI credentials are not configured (.env).")

    user_payload = {
        "user_request": message,
        "current_prompts": prompts,
        "current_steps": labels,
    }

    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    response = requests.post(
        url,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        },
        timeout=120,
        proxies={"http": None, "https": None},
    )
    response.raise_for_status()
    body = response.json()
    content = body["choices"][0]["message"]["content"]
    suggestion = json.loads(content)
    if not isinstance(suggestion, dict):
        raise RuntimeError("Suggestion is not a JSON object.")

    raw_changes = suggestion.get("changes")
    if not isinstance(raw_changes, list):
        raw_changes = []
    valid_changes = [c for c in raw_changes if isinstance(c, dict) and c.get("type") in ALLOWED_CHANGE_TYPES]

    return {
        "summary": str(suggestion.get("summary") or message),
        "notes": str(suggestion.get("notes") or ""),
        "changes": valid_changes,
        "requires_confirmation": True,
    }


def _save_history(prompts_before: dict, labels_before: dict, suggestion: dict, applied: list, skipped: list) -> None:
    history = _read_json(HISTORY_FILE, [])
    if not isinstance(history, list):
        history = []
    history.append({
        "suggestion": suggestion,
        "applied": applied,
        "skipped": skipped,
        "prompts_before": prompts_before,
        "labels_before": labels_before,
    })
    HISTORY_FILE.write_text(json.dumps(history[-20:], ensure_ascii=False, indent=2), encoding="utf-8")


def _prompt_is_referenced(key: str, steps: list) -> bool:
    def walk(value) -> bool:
        if isinstance(value, dict):
            if value.get("prompt") == key:
                return True
            return any(walk(v) for v in value.values())
        if isinstance(value, list):
            return any(walk(item) for item in value)
        return False
    return any(walk(step.get("action")) for step in steps if isinstance(step, dict))


def _insert_after(items: list, new_item: dict, after, key: str = "id") -> list:
    if after == "start":
        return [new_item] + items
    if after in (None, "end"):
        return items + [new_item]
    out = []
    inserted = False
    for item in items:
        out.append(item)
        if not inserted and item.get(key) == after:
            out.append(new_item)
            inserted = True
    if not inserted:
        out.append(new_item)
    return out


def _apply_to_steps(steps: list, change: dict) -> list:
    ctype = change["type"]

    if ctype == "add_step":
        new_step = {
            "id": change["id"],
            "title": change.get("title", change["id"]),
            "detail": change.get("detail", ""),
            "substeps": [
                {"id": s["id"], "label": s.get("label", s["id"])}
                for s in (change.get("substeps") or [])
                if isinstance(s, dict) and s.get("id")
            ],
        }
        if isinstance(change.get("stages"), list):
            new_step["stages"] = change["stages"]
        if isinstance(change.get("action"), dict) and "type" in change["action"]:
            new_step["action"] = change["action"]
        if any(s.get("id") == new_step["id"] for s in steps):
            raise RuntimeError(f"step id already exists: {new_step['id']}")
        return _insert_after(steps, new_step, change.get("after", "end"))

    if ctype == "remove_step":
        target_id = change["id"]
        if not any(s.get("id") == target_id for s in steps):
            raise RuntimeError(f"step not found: {target_id}")
        return [s for s in steps if s.get("id") != target_id]

    if ctype == "update_step":
        target_id = change["id"]
        out = []
        found = False
        for s in steps:
            if s.get("id") == target_id:
                found = True
                s = dict(s)
                if "title" in change:
                    s["title"] = change["title"]
                if "detail" in change:
                    s["detail"] = change["detail"]
                if "stages" in change and isinstance(change["stages"], list):
                    s["stages"] = change["stages"]
            out.append(s)
        if not found:
            raise RuntimeError(f"step not found: {target_id}")
        return out

    if ctype == "update_step_action":
        target_id = change["id"]
        new_action = change.get("action")
        if not isinstance(new_action, dict) or "type" not in new_action:
            raise RuntimeError("update_step_action requires action with type")
        out = []
        found = False
        for s in steps:
            if s.get("id") == target_id:
                found = True
                s = dict(s)
                s["action"] = new_action
            out.append(s)
        if not found:
            raise RuntimeError(f"step not found: {target_id}")
        return out

    if ctype == "reorder_steps":
        order = change.get("order") or []
        index = {s.get("id"): s for s in steps}
        if set(order) != set(index.keys()) or len(order) != len(index):
            raise RuntimeError("reorder_steps order must be a permutation of existing step ids")
        return [index[i] for i in order]

    if ctype in {"add_substep", "remove_substep", "update_substep"}:
        step_id = change["step_id"]
        out = []
        found = False
        for s in steps:
            if s.get("id") != step_id:
                out.append(s)
                continue
            found = True
            s = dict(s)
            subs = list(s.get("substeps") or [])
            if ctype == "add_substep":
                sub = change.get("sub") or {}
                if not sub.get("id"):
                    raise RuntimeError("add_substep requires sub.id")
                sub_obj = {"id": sub["id"], "label": sub.get("label", sub["id"])}
                if any(x.get("id") == sub_obj["id"] for x in subs):
                    raise RuntimeError(f"substep already exists: {sub_obj['id']}")
                subs = _insert_after(subs, sub_obj, change.get("after", "end"))
            elif ctype == "remove_substep":
                sub_id = change["sub_id"]
                if not any(x.get("id") == sub_id for x in subs):
                    raise RuntimeError(f"substep not found: {sub_id}")
                subs = [x for x in subs if x.get("id") != sub_id]
            else:
                sub_id = change["sub_id"]
                merged = []
                matched = False
                for x in subs:
                    if x.get("id") == sub_id:
                        matched = True
                        x = dict(x)
                        if "label" in change:
                            x["label"] = change["label"]
                    merged.append(x)
                if not matched:
                    raise RuntimeError(f"substep not found: {sub_id}")
                subs = merged
            s["substeps"] = subs
            out.append(s)
        if not found:
            raise RuntimeError(f"step not found: {step_id}")
        return out

    raise RuntimeError(f"unsupported step change type: {ctype}")


def apply_suggestion(suggestion: dict) -> dict:
    prompts_before = _read_json(PROMPTS_FILE, {})
    if not isinstance(prompts_before, dict):
        prompts_before = {}
    labels_before = _read_json(LABELS_FILE, {"section_title": "Workflow Progress", "steps": []})
    if not isinstance(labels_before, dict):
        labels_before = {"section_title": "Workflow Progress", "steps": []}

    prompts = dict(prompts_before)
    labels = dict(labels_before)
    steps = list(labels.get("steps") or [])
    steps_touched = False

    applied = []
    skipped = []

    for change in suggestion.get("changes", []):
        ctype = change.get("type")
        try:
            if ctype not in ALLOWED_CHANGE_TYPES:
                raise RuntimeError(f"unsupported change type: {ctype}")
            if ctype == "replace_prompt":
                target = change.get("target")
                if target not in prompts:
                    raise RuntimeError(f"unknown prompt target: {target}")
                prompts[target] = str(change.get("value", ""))
            elif ctype == "append_prompt_instruction":
                target = change.get("target")
                if target not in prompts:
                    raise RuntimeError(f"unknown prompt target: {target}")
                prompts[target] = prompts[target].rstrip() + "\n\n" + str(change.get("value", ""))
            elif ctype == "add_prompt":
                key = change.get("key")
                if not isinstance(key, str) or not key:
                    raise RuntimeError("add_prompt requires non-empty key")
                if key in prompts:
                    raise RuntimeError(f"prompt key already exists: {key}")
                prompts[key] = str(change.get("value", ""))
            elif ctype == "remove_prompt":
                key = change.get("key")
                if key not in prompts:
                    raise RuntimeError(f"prompt key not found: {key}")
                if _prompt_is_referenced(key, steps):
                    raise RuntimeError(f"prompt {key} is referenced by an existing step.action; remove the reference first")
                del prompts[key]
            elif ctype in STEP_CHANGE_TYPES:
                steps = _apply_to_steps(steps, change)
                steps_touched = True
            else:
                raise RuntimeError(f"unsupported change type: {ctype}")
            applied.append(change)
        except Exception as exc:
            skipped.append({"change": change, "error": str(exc)})

    labels["steps"] = steps

    PROMPTS_FILE.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    LABELS_FILE.write_text(json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8")
    _save_history(prompts_before, labels_before, suggestion, applied, skipped)

    return {
        "applied": applied,
        "skipped": skipped,
        "prompts": prompts,
        "labels": labels,
        "steps_touched": steps_touched,
    }


def undo_last() -> dict:
    history = _read_json(HISTORY_FILE, [])
    if not isinstance(history, list) or not history:
        raise RuntimeError("Nothing to undo.")
    entry = history.pop()
    prompts_before = entry.get("prompts_before") or {}
    labels_before = entry.get("labels_before") or {"section_title": "Workflow Progress", "steps": []}

    PROMPTS_FILE.write_text(json.dumps(prompts_before, ensure_ascii=False, indent=2), encoding="utf-8")
    LABELS_FILE.write_text(json.dumps(labels_before, ensure_ascii=False, indent=2), encoding="utf-8")
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

    steps_touched = bool(entry.get("applied")) and any(
        c.get("type") in {"add_step", "remove_step", "update_step", "reorder_steps",
                          "add_substep", "remove_substep", "update_substep"}
        for c in entry["applied"]
    )
    return {
        "restored_summary": entry.get("suggestion", {}).get("summary", ""),
        "prompts": prompts_before,
        "labels": labels_before,
        "steps_touched": steps_touched,
        "remaining_history": len(history),
    }
