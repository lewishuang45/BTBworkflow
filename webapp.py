import json
import os
import shutil
import subprocess
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import assistant

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "workflow_state.json"
LOG_FILE = ROOT / "workflow.log"
OUTPUT_JSON = ROOT / "final_output.json"
OUTPUT_IMAGE = ROOT / "ppt_mockup.png"
OUTPUT_MOCK_PRESENTATION = ROOT / "mock_presentation.html"
OUTPUT_BOUNDARY = ROOT / "image_soft_boundary.json"
OUTPUT_HTML = ROOT / "report_output.html"
PROMPTS_FILE = ROOT / "workflow_prompts.json"
LABELS_FILE = ROOT / "workflow_labels.json"
ASSISTANT_FILE = ROOT / "workflow_assistant_state.json"
PROBE_FILE = ROOT / "image_probe.png"
SCHEMA_FILE = ROOT / "dataset_schema.json"
TEMPLATE_FILE = ROOT / "analysis_template.json"
DATASETS_DIR = ROOT / "datasets"
TEMPLATES_DIR = ROOT / "templates"


def list_dataset_files():
    files = []
    datasets_dir = ROOT / "datasets"
    if datasets_dir.exists():
        for path in sorted(datasets_dir.glob("*.csv")):
            files.append(f"datasets/{path.name}")
        for path in sorted(datasets_dir.glob("*.xlsx")):
            files.append(f"datasets/{path.name}")
    for path in sorted(ROOT.glob("*.csv")):
        files.append(path.name)
    for path in sorted(ROOT.glob("*.xlsx")):
        files.append(path.name)
    return files


def list_template_files():
    files = []
    templates_dir = ROOT / "templates"
    if templates_dir.exists():
        for path in sorted(templates_dir.glob("*.json")):
            files.append(f"templates/{path.name}")
    for path in sorted(ROOT.glob("*template*.json")):
        files.append(path.name)
    return files


def load_template_catalog():
    catalog = []
    for name in list_template_files():
        payload = safe_json_load(ROOT / name, None)
        if isinstance(payload, dict):
            catalog.append({
                "file": name,
                "template_id": payload.get("template_id", name),
                "name": payload.get("name", name),
                "description": payload.get("description", ""),
                "expected_fields": payload.get("expected_fields", []),
                "recommended_schema": payload.get("recommended_schema", {}),
            })
    return catalog

DEFAULT_PROMPTS = {
    "prompt_1": "??????????????????????????Individual,AI,CoachedAI,AugPair,Team,AugT?????????????????ID????Team?AugT???????????????????????Individual???????top?average?bottom????33.3%?",
    "prompt_2": "????pd??????????????????????????Top???????????????????????????????????????????????AugPair?33.3%?Top??????????????????????????????????JSON?????",
    "prompt_3": "??????JSON???????????????1?PPT?????????????????????Top???????????????????????????????????JSON????????????????????????????",
    "prompt_4": "????JSON????????????????????????prompt???????PPT???????????Top???????????????????????????????????????????????????????",
}

state_lock = threading.Lock()
current_process = None


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_json_load(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return fallback


def load_prompts():
    if not PROMPTS_FILE.exists():
        PROMPTS_FILE.write_text(json.dumps(DEFAULT_PROMPTS, ensure_ascii=False, indent=2), encoding="utf-8")
        return DEFAULT_PROMPTS.copy()
    payload = safe_json_load(PROMPTS_FILE, {})
    if not isinstance(payload, dict):
        payload = {}
    merged = DEFAULT_PROMPTS.copy()
    merged.update(payload)
    return merged


def save_prompts(prompts):
    merged = DEFAULT_PROMPTS.copy()
    if isinstance(prompts, dict):
        merged.update(prompts)
    PROMPTS_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    return merged


def load_labels():
    fallback = {
        "section_title": "Workflow Progress",
        "steps": []
    }
    data = safe_json_load(LABELS_FILE, fallback)
    return data if isinstance(data, dict) else fallback


def load_schema():
    fallback = {
        "input_file": "sampleDATA.csv",
        "id_column": "id",
        "id_strategy": "auto_increment",
        "ranking_column": "Individual",
        "metric_columns": ["Individual", "AI", "CoachedAI", "AugPair"],
        "drop_columns": ["Team", "AugT"],
        "group_labels": ["top", "average", "bottom"],
    }
    data = safe_json_load(SCHEMA_FILE, fallback)
    return data if isinstance(data, dict) else fallback


def save_schema(schema):
    payload = load_schema()
    if isinstance(schema, dict):
        payload.update(schema)
    SCHEMA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_template():
    fallback = {
        "template_id": "leaderboard_comparison",
        "name": "Leaderboard Comparison",
        "description": "Analyze ranked performance groups and generate a structured report plus presentation assets.",
        "report_prompt_keys": ["prompt_1", "prompt_2"],
        "outline_prompt_keys": ["prompt_3"],
        "image_prompt_keys": ["prompt_4"],
    }
    data = safe_json_load(TEMPLATE_FILE, fallback)
    return data if isinstance(data, dict) else fallback


def save_template(template):
    payload = load_template()
    if isinstance(template, dict):
        payload.update(template)
    TEMPLATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def activate_template_file(template_file: str):
    source = ROOT / template_file
    if not source.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")
    shutil.copyfile(source, TEMPLATE_FILE)
    return load_template()


def save_uploaded_dataset(file_name: str, content_base64: str):
    import base64
    DATASETS_DIR.mkdir(exist_ok=True)
    safe_name = Path(file_name).name
    target = DATASETS_DIR / safe_name
    target.write_bytes(base64.b64decode(content_base64))
    return f"datasets/{safe_name}"


def render_report_html(report_payload):
    report_text = json.dumps(report_payload, ensure_ascii=False, indent=2)
    chart_config = ((report_payload or {}).get("report") or {}).get("chart_config")
    chart_text = json.dumps(chart_config, ensure_ascii=False, indent=2) if chart_config else "No chart config"
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BTBworkflow Report</title>
  <style>
    body {{ font-family: Inter, Arial, sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; }}
    .card {{ background:#fff; border-radius:16px; padding:20px; box-shadow:0 8px 24px rgba(15,23,42,.08); margin-bottom:16px; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background:#0f172a; color:#e2e8f0; padding:16px; border-radius:12px; overflow:auto; }}
    h1,h2 {{ margin-top:0; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>BTBworkflow Report Export</h1>
      <p>Static HTML export generated from the latest workflow output.</p>
    </div>
    <div class="card">
      <h2>Chart Config</h2>
      <pre>{chart_text}</pre>
    </div>
    <div class="card">
      <h2>Full Report JSON</h2>
      <pre>{report_text}</pre>
    </div>
  </div>
</body>
</html>
"""
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    return OUTPUT_HTML


def default_steps():
    labels = load_labels()
    steps = []
    for item in labels.get("steps", []):
        steps.append({
            "id": item["id"],
            "title": item["title"],
            "detail": item["detail"],
            "status": "pending",
            "substeps": [
                {"id": sub["id"], "label": sub["label"], "status": "pending"}
                for sub in item.get("substeps", [])
            ],
        })
    return steps


def default_state():
    return {
        "status": "idle",
        "mode": "none",
        "manual_reset": False,
        "started_at": None,
        "updated_at": now_text(),
        "message": "Ready",
        "last_exit_code": None,
        "active_step": None,
        "active_substep": None,
        "steps": default_steps(),
        "artifacts": {
            "input_csv": "sampleDATA.csv",
            "report_json": "final_output.json",
            "image_boundary": "image_soft_boundary.json",
            "ppt_image": "ppt_mockup.png",
        },
        "prompts": load_prompts(),
    }


def load_state():
    base = default_state()
    if not STATE_FILE.exists():
        return base
    payload = safe_json_load(STATE_FILE, base)
    if not isinstance(payload, dict):
        return base
    merged = base.copy()
    merged.update(payload)
    merged["steps"] = payload.get("steps") if isinstance(payload.get("steps"), list) and payload.get("steps") else base["steps"]
    merged["artifacts"] = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) and payload.get("artifacts") else base["artifacts"]
    merged["prompts"] = load_prompts()
    return merged


def save_state(state):
    with state_lock:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def append_log(message):
    previous = LOG_FILE.read_text(encoding="utf-8", errors="replace") if LOG_FILE.exists() else ""
    LOG_FILE.write_text(previous + f"[{now_text()}] {message}\n", encoding="utf-8")


def read_log_text():
    if not LOG_FILE.exists():
        return ""
    return LOG_FILE.read_text(encoding="utf-8", errors="replace")


def load_assistant_state():
    return safe_json_load(ASSISTANT_FILE, {"last_request": "", "last_suggestion": None, "updated_at": None})


def save_assistant_state(payload):
    ASSISTANT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def set_running(stage, message):
    state = load_state()
    state["status"] = "running"
    state["mode"] = stage
    state["message"] = message
    state["started_at"] = now_text()
    state["updated_at"] = now_text()
    save_state(state)


def set_finished(stage, ok, exit_code):
    state = load_state()
    state["status"] = "completed" if ok else "failed"
    state["mode"] = stage
    state["message"] = f"{stage} {'completed' if ok else 'failed'}"
    state["updated_at"] = now_text()
    state["last_exit_code"] = exit_code
    save_state(state)


def run_command(args, stage):
    global current_process
    set_running(stage, f"Running {stage} workflow")
    current_process = subprocess.Popen(args, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=False)
    assert current_process.stdout is not None
    for raw in iter(current_process.stdout.readline, b""):
        if not raw:
            break
        append_log(raw.decode("utf-8", errors="replace").rstrip())
    exit_code = current_process.wait()
    set_finished(stage, exit_code == 0, exit_code)
    current_process = None


def run_report_chain():
    run_command(["python", "run_workflow.py", "--stage", "report"], "report")


def run_image_chain():
    run_command(["python", "run_workflow.py", "--stage", "image"], "image")


def run_image_probe():
    proc = subprocess.run(["python", "probe_image2.py"], cwd=str(ROOT), capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    append_log(output.strip())
    return {
        "ok": proc.returncode == 0 and PROBE_FILE.exists(),
        "exit_code": proc.returncode,
        "output": output,
        "probe_file": PROBE_FILE.name if PROBE_FILE.exists() else None,
    }


def restore_state_from_artifacts():
    state = load_state()
    if state.get("manual_reset"):
        return state
    return state


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if content_type.startswith("image/"):
            self.send_header("Cache-Control", "no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            return self._send_file(ROOT / "webui" / "index.html", "text/html; charset=utf-8")
        if path == "/app.js":
            return self._send_file(ROOT / "webui" / "app.js", "application/javascript; charset=utf-8")
        if path == "/style.css":
            return self._send_file(ROOT / "webui" / "style.css", "text/css; charset=utf-8")
        if path == "/preview-image":
            if OUTPUT_IMAGE.exists():
                return self._send_file(OUTPUT_IMAGE, "image/png")
            self.send_error(404)
            return
        if path == "/mock-presentation":
            if OUTPUT_MOCK_PRESENTATION.exists():
                return self._send_file(OUTPUT_MOCK_PRESENTATION, "text/html; charset=utf-8")
            self.send_error(404)
            return
        if path == "/report-output":
            if OUTPUT_HTML.exists():
                return self._send_file(OUTPUT_HTML, "text/html; charset=utf-8")
            self.send_error(404)
            return
        if path == "/preview-probe":
            if PROBE_FILE.exists():
                return self._send_file(PROBE_FILE, "image/png")
            self.send_error(404)
            return
        if path == "/api/state":
            return self._json({
                "state": restore_state_from_artifacts(),
                "assistant": load_assistant_state(),
                "schema": load_schema(),
                "template": load_template(),
                "dataset_files": list_dataset_files(),
                "template_files": list_template_files(),
                "template_catalog": load_template_catalog(),
                "log": read_log_text(),
                "report_preview": safe_json_load(OUTPUT_JSON, None) if OUTPUT_JSON.exists() else None,
                "dataset_preview": (safe_json_load(OUTPUT_JSON, None) or {}).get("report", {}).get("dataset_preview") if OUTPUT_JSON.exists() else None,
                "chart_config": (safe_json_load(OUTPUT_JSON, None) or {}).get("report", {}).get("chart_config") if OUTPUT_JSON.exists() else None,
                "has_report": OUTPUT_JSON.exists(),
                "has_boundary": OUTPUT_BOUNDARY.exists(),
                "has_image": OUTPUT_IMAGE.exists(),
                "has_presentation_artifact": OUTPUT_IMAGE.exists() or OUTPUT_MOCK_PRESENTATION.exists(),
                "has_probe": PROBE_FILE.exists(),
                "has_html_report": OUTPUT_HTML.exists(),
                "image_url": "/preview-image" if OUTPUT_IMAGE.exists() else None,
                "presentation_url": "/preview-image" if OUTPUT_IMAGE.exists() else ("/mock-presentation" if OUTPUT_MOCK_PRESENTATION.exists() else None),
                "probe_url": "/preview-probe" if PROBE_FILE.exists() else None,
                "html_report_url": "/report-output" if OUTPUT_HTML.exists() else None,
            })
        self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length else b""
        try:
            body = json.loads(raw.decode("utf-8-sig")) if raw else {}
        except Exception:
            body = {}

        if self.path == "/api/prompts":
            saved = save_prompts(body.get("prompts", {}))
            state = load_state()
            state["prompts"] = saved
            save_state(state)
            return self._json({"ok": True, "prompts": saved})
        if self.path == "/api/schema":
            saved = save_schema(body.get("schema", {}))
            state = load_state()
            state["artifacts"]["input_csv"] = saved.get("input_file", state["artifacts"].get("input_csv", "sampleDATA.csv"))
            save_state(state)
            return self._json({"ok": True, "schema": saved})
        if self.path == "/api/template":
            template_file = body.get("template_file")
            if template_file:
                saved = activate_template_file(template_file)
            else:
                saved = save_template(body.get("template", {}))
            return self._json({"ok": True, "template": saved})
        if self.path == "/api/datasets/upload":
            file_name = body.get("file_name", "").strip()
            content_base64 = body.get("content_base64", "")
            if not file_name or not content_base64:
                return self._json({"ok": False, "message": "file_name and content_base64 are required"}, 400)
            stored_file = save_uploaded_dataset(file_name, content_base64)
            schema = save_schema({"input_file": stored_file})
            state = load_state()
            state["artifacts"]["input_csv"] = stored_file
            save_state(state)
            return self._json({"ok": True, "stored_file": stored_file, "schema": schema})
        if self.path == "/api/export/html":
            if not OUTPUT_JSON.exists():
                return self._json({"ok": False, "message": "No report output available to export"}, 400)
            payload = safe_json_load(OUTPUT_JSON, None)
            render_report_html(payload)
            return self._json({"ok": True, "html_report_url": "/report-output"})
        if self.path == "/api/prompts/reset":
            saved = save_prompts(DEFAULT_PROMPTS)
            state = default_state()
            state["prompts"] = saved
            save_state(state)
            return self._json({"ok": True, "prompts": saved})
        if self.path == "/api/dashboard/reset":
            state = default_state()
            state["manual_reset"] = True
            save_state(state)
            return self._json({"ok": True, "state": state})
        if self.path == "/api/probe/image":
            result = run_image_probe()
            return self._json(result, 200 if result.get("ok") else 500)
        if self.path == "/api/assistant/suggest":
            message = body.get("message", "").strip()
            if not message:
                return self._json({"ok": False, "message": "Message is required"}, 400)
            try:
                suggestion = assistant.request_suggestion(message, load_prompts(), load_labels())
            except Exception as exc:
                return self._json({"ok": False, "message": f"Assistant request failed: {exc}"}, 500)
            save_assistant_state({"last_request": message, "last_suggestion": suggestion, "updated_at": now_text()})
            return self._json({"ok": True, "suggestion": suggestion})
        if self.path == "/api/assistant/undo":
            try:
                result = assistant.undo_last()
            except Exception as exc:
                return self._json({"ok": False, "message": f"Undo failed: {exc}"}, 400)
            state = load_state()
            state["prompts"] = result["prompts"]
            if result.get("steps_touched"):
                state["steps"] = default_steps()
                state["active_step"] = None
                state["active_substep"] = None
            save_state(state)
            return self._json({
                "ok": True,
                "restored_summary": result["restored_summary"],
                "prompts": result["prompts"],
                "remaining_history": result["remaining_history"],
                "steps_touched": result["steps_touched"],
            })
        if self.path == "/api/assistant/apply":
            suggestion = body.get("suggestion") or {}
            try:
                result = assistant.apply_suggestion(suggestion)
            except Exception as exc:
                return self._json({"ok": False, "message": f"Apply failed: {exc}"}, 500)
            state = load_state()
            state["prompts"] = result["prompts"]
            if result.get("steps_touched"):
                state["steps"] = default_steps()
                state["active_step"] = None
                state["active_substep"] = None
            save_state(state)
            return self._json({
                "ok": True,
                "prompts": result["prompts"],
                "applied": result["applied"],
                "skipped": result["skipped"],
                "steps_touched": result["steps_touched"],
            })

        state = load_state()
        if state.get("status") == "running":
            return self._json({"ok": False, "message": "A workflow is already running"}, 409)
        if self.path == "/api/run/report":
            threading.Thread(target=run_report_chain, daemon=True).start()
            return self._json({"ok": True, "message": "Report chain started"})
        if self.path == "/api/run/image":
            threading.Thread(target=run_image_chain, daemon=True).start()
            return self._json({"ok": True, "message": "Image chain started"})
        self.send_error(404)


if __name__ == "__main__":
    assistant.load_dotenv()
    save_prompts(load_prompts())
    if not STATE_FILE.exists():
        save_state(default_state())
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT") or os.getenv("WEBSITES_PORT") or "8000")
    server = HTTPServer((host, port), Handler)
    print(f"Web UI running at http://{host}:{port}")
    server.serve_forever()
