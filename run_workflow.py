import argparse
import base64
import json
import math
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / "sampleDATA.csv"
OUTPUT_JSON = ROOT / "final_output.json"
OUTPUT_IMAGE = ROOT / "ppt_mockup.png"
IMAGE_BOUNDARY_FILE = ROOT / "image_soft_boundary.json"
LABELS_FILE = ROOT / "workflow_labels.json"
STATE_FILE = ROOT / "workflow_state.json"


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


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


def round_nested(value):
    if isinstance(value, float):
        return round(value, 2)
    if isinstance(value, dict):
        return {key: round_nested(item) for key, item in value.items()}
    if isinstance(value, list):
        return [round_nested(item) for item in value]
    return value


def azure_openai_request(endpoint: str, api_key: str, api_version: str, deployment: str, payload: dict) -> dict:
    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    response = requests.post(
        url,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=240,
        proxies={"http": None, "https": None},
    )
    response.raise_for_status()
    return response.json()


def azure_image_request(endpoint: str, api_key: str, api_version: str, deployment: str, prompt: str) -> bytes:
    generations_url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/images/generations?api-version={api_version}"
    last_error = None
    session = requests.Session()
    session.trust_env = False
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=2,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    for attempt in range(3):
        try:
            print(f"[image2] attempt {attempt + 1}/8: requesting generation...", flush=True)
            response = session.post(
                generations_url,
                headers={"api-key": api_key, "Content-Type": "application/json"},
                json={"prompt": prompt, "size": "1024x1024", "quality": "medium"},
                timeout=(30, 7200),
            )
            print(f"[image2] generation status: {response.status_code}", flush=True)
            response.raise_for_status()
            data = response.json()
            image_url = data["data"][0].get("url")
            if image_url:
                print("[image2] downloading image payload...", flush=True)
                image_response = session.get(image_url, timeout=(30, 7200))
                image_response.raise_for_status()
                return image_response.content
            b64 = data["data"][0].get("b64_json")
            if b64:
                return base64.b64decode(b64)
            raise RuntimeError("Image generation returned no image payload.")
        except Exception as exc:
            last_error = exc
            print(f"[image2] attempt failed: {exc}", flush=True)
            time.sleep(min(5 * (attempt + 1), 15))

    message = str(last_error)
    if "401" in message or "PermissionDenied" in message:
        raise RuntimeError(f"Image authentication failed: {last_error}")
    if "RemoteDisconnected" in message or "Connection aborted" in message:
        raise RuntimeError(f"Image connection dropped before response: {last_error}")
    if "timed out" in message or "ReadTimeout" in message:
        raise RuntimeError(f"Image request timed out: {last_error}")
    raise RuntimeError(f"Image generation failed after retries: {last_error}")


def assign_groups(df: pd.DataFrame) -> pd.DataFrame:
    ranked = df.sort_values(["Individual", "id"], ascending=[False, True]).reset_index(drop=True)
    total = len(ranked)
    top_count = math.ceil(total / 3)
    bottom_count = math.floor(total / 3)
    average_cutoff = total - bottom_count
    labels = []
    for idx in range(total):
        if idx < top_count:
            labels.append("top")
        elif idx >= average_cutoff:
            labels.append("bottom")
        else:
            labels.append("average")
    ranked["group"] = labels
    return ranked.sort_values("id").reset_index(drop=True)


def prepare_dataset() -> dict:
    df = pd.read_csv(INPUT_CSV)
    expected = ["Individual", "AI", "CoachedAI", "AugPair", "Team", "AugT"]
    if list(df.columns) != expected:
        raise RuntimeError(f"Unexpected columns: {list(df.columns)}")
    df = df.copy()
    df.insert(0, "id", range(1, len(df) + 1))
    cleaned = df.drop(columns=["Team", "AugT"])
    grouped = assign_groups(cleaned)
    summary = {
        "row_count": int(len(grouped)),
        "columns": grouped.columns.tolist(),
        "group_counts": grouped["group"].value_counts().to_dict(),
        "individual_quantiles": {
            "q25": float(grouped["Individual"].quantile(0.25)),
            "q50": float(grouped["Individual"].quantile(0.5)),
            "q75": float(grouped["Individual"].quantile(0.75)),
        },
        "records": grouped.to_dict(orient="records"),
    }
    return round_nested(summary)


def extract_json(text: str) -> dict:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Model did not return valid JSON.")
    return json.loads(text[start : end + 1])


def _extract_image_fields(outline_report: dict) -> dict:
    slide = outline_report.get("slide", {}) if isinstance(outline_report, dict) else {}
    title = slide.get("title") or outline_report.get("page_title") or "Top Group Four-Round Performance"
    subtitle = slide.get("subtitle") or outline_report.get("page_subtitle") or "Single-slide business report"
    core_message = slide.get("core_message") or outline_report.get("core_message") or "Focus on Top group performance, stability, final average score, and overlap rate."

    metrics = []
    for item in ((slide.get("sections", []) if isinstance(slide, dict) else []) or []):
        if item.get("type") == "key_metrics":
            for metric in item.get("items", [])[:4]:
                metrics.append(f"{metric.get('label')}: {metric.get('value')}{metric.get('unit', '')}")
            break
    return {
        "title": title,
        "subtitle": subtitle,
        "core_message": core_message,
        "metrics": metrics[:4],
    }


def _build_report_number_boundary() -> str:
    return (
        "Data boundary: use only numbers already present in the preceding report JSON, including "
        "dataset totals, group sizes, percentages, means, overlap counts, and overlap rates. "
        "Do not invent new counts, proportions, sample sizes, or totals. If the report JSON does "
        "not clearly provide a number, omit that number from the image rather than guessing. "
        "The grouping logic is: add a natural-order ID, drop Team and AugT, sort Individual "
        "descending, then split the cleaned rows into Top, Average, and Bottom thirds, each about "
        "one third of the dataset."
    )


def _boundary_to_text(boundary) -> str:
    if not boundary:
        return ""
    if isinstance(boundary, str):
        return boundary.strip()
    if not isinstance(boundary, dict):
        return str(boundary)

    parts = []
    prompt_text = boundary.get("prompt_text") or boundary.get("image_prompt_boundary")
    if prompt_text:
        parts.append(str(prompt_text))

    for key in [
        "authoritative_numbers",
        "authoritative_values",
        "chart_value_rules",
        "table_rules",
        "forbidden_claims",
        "stability_definition_rules",
        "overlap_rules",
        "missing_number_policy",
        "final_round_claim_policy",
        "wording_rules",
    ]:
        value = boundary.get(key)
        if not value:
            continue
        parts.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")

    if not parts:
        parts.append(json.dumps(boundary, ensure_ascii=False))
    return "Image soft boundary from the report: " + " ".join(parts)


def load_image_boundary_text() -> str:
    boundary = _read_json_safe(IMAGE_BOUNDARY_FILE, None)
    text = _boundary_to_text(boundary)
    return text if text else ""


def _build_report_facts_text(outline_report: dict) -> str:
    chart_data = outline_report.get("chart_ready_data", {}) if isinstance(outline_report, dict) else {}
    if not isinstance(chart_data, dict):
        return ""

    facts = []
    line_chart = chart_data.get("line_chart_data", {})
    if isinstance(line_chart, dict):
        categories = line_chart.get("categories") or []
        series = line_chart.get("series") or []
        if categories and isinstance(series, list):
            for item in series:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                values = item.get("values")
                if name and isinstance(values, list) and len(values) == len(categories):
                    pairs = "; ".join(f"{cat}={val}" for cat, val in zip(categories, values))
                    facts.append(f"{name} round means: {pairs}.")

    sample_info = chart_data.get("sample_info", {})
    group_sizes = sample_info.get("group_sizes", {}) if isinstance(sample_info, dict) else {}
    total_n = sample_info.get("total_n") if isinstance(sample_info, dict) else None
    if total_n or group_sizes:
        facts.append(
            "Sample info: "
            f"total_n={total_n}; "
            f"Top n={group_sizes.get('top')}; "
            f"Average n={group_sizes.get('average')}; "
            f"Bottom n={group_sizes.get('bottom')}."
        )
    else:
        facts.append("Do not display a total-records number unless the report JSON explicitly provides it.")

    top_means = chart_data.get("top_group_round_means", {})
    if isinstance(top_means, dict) and top_means:
        facts.append(
            "Top round means: "
            f"Individual={top_means.get('Individual')}; "
            f"AI={top_means.get('AI')}; "
            f"CoachedAI={top_means.get('CoachedAI')}; "
            f"AugPair={top_means.get('AugPair')}."
        )

    final_cmp = chart_data.get("final_round_comparison", {})
    augpair_means = final_cmp.get("augpair_means", {}) if isinstance(final_cmp, dict) else {}
    if isinstance(augpair_means, dict) and augpair_means:
        facts.append(
            "Final-round AugPair means: "
            f"Top={augpair_means.get('top')}; "
            f"Average={augpair_means.get('average')}; "
            f"Bottom={augpair_means.get('bottom')}. "
            "Do not claim Top is highest in the final round unless this comparison shows it."
        )
    final_mean_comparison = chart_data.get("final_mean_comparison_data", {})
    if isinstance(final_mean_comparison, dict):
        categories = final_mean_comparison.get("categories") or []
        values = final_mean_comparison.get("values") or []
        if categories and values and len(categories) == len(values):
            pairs = "; ".join(f"{cat}={val}" for cat, val in zip(categories, values))
            facts.append(
                "Final-round group means: "
                f"{pairs}. "
                "Use this exact ordering and do not claim Top is the final-round leader unless its value is the largest."
            )

    overall_mean = chart_data.get("overall_4round_mean", {})
    if isinstance(overall_mean, dict) and overall_mean:
        facts.append(
            "Overall four-round means: "
            f"Top={overall_mean.get('top')}; "
            f"Average={overall_mean.get('average')}; "
            f"Bottom={overall_mean.get('bottom')}."
        )

    stability = chart_data.get("stability_metrics", {})
    player_fluctuation = stability.get("player_level_fluctuation", {}) if isinstance(stability, dict) else {}
    mean_std = player_fluctuation.get("mean_std_across_4_rounds", {}) if isinstance(player_fluctuation, dict) else {}
    if isinstance(mean_std, dict) and mean_std:
        facts.append(
            "Player-level fluctuation mean std across four rounds: "
            f"Top={mean_std.get('top')}; "
            f"Average={mean_std.get('average')}; "
            f"Bottom={mean_std.get('bottom')}."
        )
    stability_comparison = chart_data.get("stability_comparison_data", {})
    if isinstance(stability_comparison, dict):
        categories = stability_comparison.get("categories") or []
        ranges = stability_comparison.get("range_of_round_means") or []
        within_stds = stability_comparison.get("avg_within_group_std") or []
        if categories and ranges and len(categories) == len(ranges):
            pairs = "; ".join(f"{cat}={val}" for cat, val in zip(categories, ranges))
            facts.append(f"Stability by range of round means: {pairs}.")
        if categories and within_stds and len(categories) == len(within_stds):
            pairs = "; ".join(f"{cat}={val}" for cat, val in zip(categories, within_stds))
            facts.append(
                f"Average within-group standard deviation: {pairs}. "
                "When describing stability, specify which stability metric is being used."
            )

    overlap = chart_data.get("overlap_metrics", {})
    if isinstance(overlap, dict) and overlap:
        facts.append(
            "Overlap metrics: "
            f"top_group_size={overlap.get('top_group_size')}; "
            f"augpair_top33_size={overlap.get('augpair_top33_size')}; "
            f"overlap_count={overlap.get('overlap_count')}; "
            f"overlap_rate_display={overlap.get('overlap_rate_display')}."
        )
    overlap_data = chart_data.get("overlap_data", {})
    if isinstance(overlap_data, dict) and overlap_data:
        facts.append(
            "Overlap data: "
            f"top_group_size={overlap_data.get('top_group_size')}; "
            f"augpair_top_size={overlap_data.get('augpair_top_37_size') or overlap_data.get('augpair_top33_size')}; "
            f"intersection_size={overlap_data.get('intersection_size')}; "
            f"overlap_rate_percent={overlap_data.get('overlap_rate_percent')}."
        )

    if not facts:
        return ""
    return "Authoritative report facts for the image. Use these values exactly; do not replace them with cleaner-looking or inferred values. " + " ".join(facts)


def build_image_prompts(outline_report: dict, prompt_4: str = "Generate a single-slide PPT-style report image.") -> list[str]:
    base = _extract_image_fields(outline_report)
    title = base["title"]
    subtitle = base["subtitle"]
    core_message = base["core_message"]
    metrics = " ; ".join(base["metrics"]) if base["metrics"] else "Highlight final score, stability, and overlap information for Top group."
    number_boundary = _build_report_number_boundary()
    report_facts = load_image_boundary_text() or _build_report_facts_text(outline_report)
    if not prompt_4:
        prompt_4 = "Generate a single-slide PPT-style report image."

    tier1 = (
        f"{prompt_4}\n\n"
        "Create a 16:9 business slide style image.\n"
        f"Title: {title}\n"
        f"Subtitle: {subtitle}\n"
        f"Core message: {core_message}\n"
        f"Key metrics: {metrics}\n"
        f"{number_boundary}\n"
        f"{report_facts}\n"
        "Must include: one line chart, one comparison chart, one key data table, and one conclusion area.\n"
        "Keep the topic focused on Top group four-round performance only.\n"
        "Professional consulting-slide style, clear hierarchy, information-dense, presentation-ready."
    )

    tier2 = (
        "Create one 16:9 business slide image about Top group four-round performance. "
        f"Title: {title}. Core message: {core_message}. "
        f"Show these metrics: {metrics}. "
        f"{number_boundary} "
        f"{report_facts} "
        "Must include a line chart, a comparison chart, a data table, and a conclusion box."
    )

    tier3 = (
        "Business slide, 16:9, Top group four-round performance. "
        f"{number_boundary} "
        f"{report_facts} "
        "Include line chart, comparison chart, small data table, and conclusion area. "
        f"Title: {title}."
    )
    return [tier1, tier2, tier3]


PROMPTS_FILE = ROOT / "workflow_prompts.json"


def _read_json_safe(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return fallback


def load_prompts_dict() -> dict:
    payload = _read_json_safe(PROMPTS_FILE, {})
    return payload if isinstance(payload, dict) else {}


def _sync_state_steps_with_labels(state: dict) -> None:
    labels = _read_json_safe(LABELS_FILE, {})
    label_steps = labels.get("steps") if isinstance(labels, dict) else None
    if not isinstance(label_steps, list):
        return

    current_steps = state.get("steps") if isinstance(state.get("steps"), list) else []
    current_by_id = {
        step.get("id"): step
        for step in current_steps
        if isinstance(step, dict) and step.get("id")
    }
    label_ids = [step.get("id") for step in label_steps if isinstance(step, dict) and step.get("id")]
    current_ids = [step.get("id") for step in current_steps if isinstance(step, dict) and step.get("id")]
    if label_ids == current_ids:
        return

    synced = []
    for label_step in label_steps:
        sid = label_step.get("id")
        if not sid:
            continue
        existing = current_by_id.get(sid, {})
        existing_substeps = {
            sub.get("id"): sub
            for sub in existing.get("substeps", [])
            if isinstance(sub, dict) and sub.get("id")
        }
        substeps = []
        for sub in label_step.get("substeps", []):
            sub_id = sub.get("id")
            if not sub_id:
                continue
            previous = existing_substeps.get(sub_id, {})
            substeps.append({
                "id": sub_id,
                "label": sub.get("label", sub_id),
                "status": previous.get("status", "pending"),
                **({"runtime_message": previous["runtime_message"]} if previous.get("runtime_message") else {}),
            })
        synced.append({
            "id": sid,
            "title": label_step.get("title", sid),
            "detail": label_step.get("detail", ""),
            "status": existing.get("status", "pending"),
            "substeps": substeps,
            **({"runtime_message": existing["runtime_message"]} if existing.get("runtime_message") else {}),
        })
    state["steps"] = synced


def update_step_state(step_id: str, status: str, message: str = "") -> None:
    state = _read_json_safe(STATE_FILE, None)
    if not isinstance(state, dict):
        return
    _sync_state_steps_with_labels(state)
    steps = state.get("steps") or []
    for step in steps:
        if step.get("id") == step_id:
            step["status"] = status
            if message:
                step["runtime_message"] = message
            for substep in step.get("substeps") or []:
                substep["status"] = status
                if message:
                    substep["runtime_message"] = message
            break
    state["active_step"] = step_id if status == "running" else state.get("active_step")
    if status == "running":
        active_step = next((step for step in steps if step.get("id") == step_id), None)
        substeps = active_step.get("substeps") if isinstance(active_step, dict) else []
        state["active_substep"] = substeps[0].get("id") if substeps else None
    if status in {"completed", "failed", "skipped"} and state.get("active_step") == step_id:
        state["active_step"] = None
        state["active_substep"] = None
    try:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def _resolve_user_parts(parts: list, ctx: dict, prompts: dict) -> str:
    out = []
    for part in parts or []:
        if not isinstance(part, dict):
            continue
        if "text" in part:
            out.append(str(part["text"]))
        elif "prompt" in part:
            out.append(str(prompts.get(part["prompt"], "")))
        elif "ctx" in part:
            value = ctx.get(part["ctx"])
            fmt = part.get("format", "json")
            if fmt == "text":
                out.append("" if value is None else str(value))
            else:
                out.append(json.dumps(value, ensure_ascii=False))
        elif "env" in part:
            out.append(str(os.getenv(part["env"], "")))
    return "".join(out)


def _resolve_template(value, output, ctx: dict):
    if isinstance(value, dict):
        if "$output" in value:
            return output
        if "$ctx" in value:
            return ctx.get(value["$ctx"])
        if "$env" in value:
            return os.getenv(value["$env"], "")
        return {k: _resolve_template(v, output, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_template(item, output, ctx) for item in value]
    return value


def _do_save_to(spec: dict, output, ctx: dict) -> None:
    file_name = spec.get("file")
    if not file_name:
        return
    file_path = ROOT / file_name
    if "wrap" in spec:
        wrapped = _resolve_template(spec["wrap"], output, ctx)
    elif "from_ctx" in spec:
        wrapped = ctx.get(spec["from_ctx"])
    else:
        wrapped = output
    file_path.write_text(json.dumps(round_nested(wrapped), ensure_ascii=False, indent=2), encoding="utf-8")


def _do_patch_json(spec: dict, ctx: dict) -> None:
    file_name = spec.get("file")
    if not file_name:
        return
    file_path = ROOT / file_name
    if not file_path.exists():
        raise RuntimeError(f"patch target not found: {file_name}")
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    patch = _resolve_template(spec.get("patch", {}), None, ctx)
    if isinstance(payload, dict) and isinstance(patch, dict):
        payload.update(patch)
        file_path.write_text(json.dumps(round_nested(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def action_load_env(action: dict, ctx: dict) -> None:
    ctx["text_endpoint"] = require_env("AZURE_OPENAI_ENDPOINT")
    ctx["text_key"] = require_env("AZURE_OPENAI_API_KEY")
    ctx["text_api_version"] = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    ctx["text_deployment"] = require_env("AZURE_OPENAI_TEXT_DEPLOYMENT")
    ctx["image_endpoint"] = os.getenv("AZURE_OPENAI_IMAGE_ENDPOINT", ctx["text_endpoint"])
    ctx["image_key"] = os.getenv("AZURE_OPENAI_IMAGE_API_KEY", ctx["text_key"])
    ctx["image_api_version"] = os.getenv("AZURE_OPENAI_IMAGE_API_VERSION", ctx["text_api_version"])
    ctx["image_deployment"] = require_env("AZURE_OPENAI_IMAGE_DEPLOYMENT")


def action_prepare_dataset(action: dict, ctx: dict) -> None:
    output_to = action.get("output_to", "data_summary")
    ctx[output_to] = prepare_dataset()


def action_llm_text(action: dict, ctx: dict) -> None:
    user_message = _resolve_user_parts(action.get("user_parts", []), ctx, ctx.get("_prompts", {}))
    system = action.get("system", "")
    temperature = action.get("temperature", 0.2)
    response_format = action.get("response_format", "json_object")
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
    }
    if response_format == "json_object":
        payload["response_format"] = {"type": "json_object"}
    response = azure_openai_request(
        ctx["text_endpoint"], ctx["text_key"], ctx["text_api_version"],
        ctx["text_deployment"], payload,
    )
    raw = response["choices"][0]["message"]["content"]
    if response_format == "json_object":
        output = round_nested(extract_json(raw))
    else:
        output = raw
    output_to = action.get("output_to")
    if output_to:
        ctx[output_to] = output
    save_to = action.get("save_to")
    if isinstance(save_to, dict):
        _do_save_to(save_to, output, ctx)


def action_build_image_boundary(action: dict, ctx: dict) -> None:
    input_from = action.get("input_from", "outline_report")
    fallback_file = action.get("fallback_file", "final_output.json")
    output_to = action.get("output_to", "image_soft_boundary")
    output_file = action.get("output_file", "image_soft_boundary.json")

    if input_from in ctx:
        report = ctx[input_from]
    elif fallback_file and (ROOT / fallback_file).exists():
        payload = json.loads((ROOT / fallback_file).read_text(encoding="utf-8-sig"))
        if not isinstance(payload, dict) or "report" not in payload:
            raise RuntimeError(f"{fallback_file} does not contain report content.")
        ctx["final_output"] = payload
        report = payload["report"]
    else:
        raise RuntimeError(f"build_image_boundary requires '{input_from}' in context or fallback_file")

    system = (
        "You are a data-boundary editor for image generation. Read the report JSON and extract "
        "only the constraints that an image model must obey. Do not recalculate the data and do "
        "not add facts that are absent from the report. Return strict JSON only."
    )
    user_message = (
        "Create an image-generation soft boundary from this report JSON. The boundary must help "
        "a chart-heavy business slide avoid fabricated numbers, wrong rankings, unsupported "
        "claims, and invented sample sizes. If the report lacks a value, say that the image must "
        "omit it instead of guessing.\n\n"
        "Return JSON with this shape:\n"
        "{\n"
        '  "summary": "short description",\n'
        '  "authoritative_values": ["exact values and labels that may be shown"],\n'
        '  "chart_value_rules": ["rules for line charts, comparison charts, and tables"],\n'
        '  "forbidden_claims": ["claims the image must not make"],\n'
        '  "stability_definition_rules": ["how stability may be described"],\n'
        '  "overlap_rules": ["how overlap counts/rates may be shown"],\n'
        '  "missing_number_policy": "policy for absent values",\n'
        '  "final_round_claim_policy": "policy for final-round leadership claims",\n'
        '  "prompt_text": "compact natural-language boundary to insert into an image prompt"\n'
        "}\n\n"
        f"Report JSON:\n{json.dumps(report, ensure_ascii=False)}"
    )
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        "temperature": action.get("temperature", 0.1),
        "response_format": {"type": "json_object"},
    }
    response = azure_openai_request(
        ctx["text_endpoint"], ctx["text_key"], ctx["text_api_version"],
        ctx["text_deployment"], payload,
    )
    raw = response["choices"][0]["message"]["content"]
    boundary = round_nested(extract_json(raw))
    ctx[output_to] = boundary
    (ROOT / output_file).write_text(json.dumps(boundary, ensure_ascii=False, indent=2), encoding="utf-8")


def action_build_image_prompts(action: dict, ctx: dict) -> None:
    input_from = action.get("input_from", "outline_report")
    output_to = action.get("output_to", "image_prompts")
    fallback_file = action.get("fallback_file")
    if input_from in ctx:
        report = ctx[input_from]
    elif fallback_file and (ROOT / fallback_file).exists():
        payload = json.loads((ROOT / fallback_file).read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or "report" not in payload:
            raise RuntimeError(f"{fallback_file} does not contain report content.")
        ctx["final_output"] = payload
        report = payload["report"]
    else:
        raise RuntimeError(f"build_image_prompts requires '{input_from}' in context or fallback_file")
    prompt_4 = ctx.get("_prompts", {}).get("prompt_4", "")
    ctx[output_to] = build_image_prompts(report, prompt_4)


def action_llm_image(action: dict, ctx: dict) -> None:
    input_from = action.get("input_from", "image_prompts")
    prompts_value = ctx.get(input_from)
    if not prompts_value:
        raise RuntimeError(f"llm_image requires '{input_from}' in context")
    if isinstance(prompts_value, str):
        prompts_value = [prompts_value]
    last_error = None
    image_bytes = None
    for index, image_prompt in enumerate(prompts_value, start=1):
        try:
            print(f"[image2] prompt tier {index}/{len(prompts_value)}", flush=True)
            image_bytes = azure_image_request(
                ctx["image_endpoint"], ctx["image_key"], ctx["image_api_version"],
                ctx["image_deployment"], image_prompt,
            )
            break
        except Exception as exc:
            last_error = exc
            print(f"[image2] tier {index} failed: {exc}", flush=True)
    if image_bytes is None:
        raise RuntimeError(f"Image generation failed across all prompt tiers: {last_error}")
    output_file = action.get("output_file", "ppt_mockup.png")
    (ROOT / output_file).write_bytes(image_bytes)
    patch_after = action.get("patch_after")
    if isinstance(patch_after, dict):
        _do_patch_json(patch_after, ctx)


def action_save_json(action: dict, ctx: dict) -> None:
    _do_save_to(action, None, ctx)


def action_patch_json(action: dict, ctx: dict) -> None:
    _do_patch_json(action, ctx)


ACTION_HANDLERS = {
    "load_env": action_load_env,
    "prepare_dataset": action_prepare_dataset,
    "llm_text": action_llm_text,
    "build_image_boundary": action_build_image_boundary,
    "build_image_prompts": action_build_image_prompts,
    "llm_image": action_llm_image,
    "save_json": action_save_json,
    "patch_json": action_patch_json,
}


def load_step_definitions() -> list:
    payload = _read_json_safe(LABELS_FILE, None)
    if isinstance(payload, dict) and isinstance(payload.get("steps"), list):
        return payload["steps"]
    return []


def run_pipeline(stage: str) -> dict:
    ctx: dict = {"_prompts": load_prompts_dict()}
    summary = {"executed": [], "skipped": [], "failed": None}
    for step in load_step_definitions():
        sid = step.get("id") or "?"
        action = step.get("action")
        stages = set(step.get("stages") or ["all"])

        if not isinstance(action, dict) or "type" not in action:
            print(f"[step] {sid}: skipped (no action defined)", flush=True)
            update_step_state(sid, "skipped", "no action defined")
            summary["skipped"].append({"id": sid, "reason": "no action defined"})
            continue
        if stage != "all" and stage not in stages and "all" not in stages:
            print(f"[step] {sid}: skipped (not in stage '{stage}')", flush=True)
            update_step_state(sid, "skipped", f"not in stage {stage}")
            summary["skipped"].append({"id": sid, "reason": f"not in stage {stage}"})
            continue
        atype = action["type"]
        handler = ACTION_HANDLERS.get(atype)
        if handler is None:
            print(f"[step] {sid}: skipped (unknown action type: {atype})", flush=True)
            update_step_state(sid, "skipped", f"unknown action type: {atype}")
            summary["skipped"].append({"id": sid, "reason": f"unknown action type: {atype}"})
            continue
        print(f"[step] {sid}: running ({atype})", flush=True)
        update_step_state(sid, "running", f"running {atype}")
        try:
            handler(action, ctx)
        except Exception as exc:
            print(f"[step] {sid}: failed - {exc}", flush=True)
            update_step_state(sid, "failed", str(exc))
            summary["failed"] = {"id": sid, "error": str(exc)}
            raise
        print(f"[step] {sid}: completed", flush=True)
        update_step_state(sid, "completed", f"{sid} ok")
        summary["executed"].append(sid)
    return summary


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["all", "report", "image"], default="all")
    args = parser.parse_args()
    summary = run_pipeline(args.stage)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
