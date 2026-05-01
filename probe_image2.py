import base64
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "image_probe.png"


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()


def main() -> None:
    load_dotenv()
    endpoint = os.environ["IMAGE_MODEL_ENDPOINT"]
    api_key = os.environ["IMAGE_MODEL_API_KEY"]
    api_version = os.environ.get("IMAGE_MODEL_API_VERSION", "2025-04-01-preview")
    deployment = os.environ["IMAGE_MODEL_DEPLOYMENT"]

    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/images/generations?api-version={api_version}"
    session = requests.Session()
    session.trust_env = False
    print(f"[probe] POST {url}", flush=True)
    response = session.post(
        url,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json={"prompt": "Create a simple business slide style image with one title box and two color blocks.", "size": "1024x1024", "quality": "medium"},
        timeout=(30, 180),
    )
    print(f"[probe] STATUS {response.status_code}", flush=True)
    response.raise_for_status()
    payload = response.json()
    item = payload["data"][0]
    if item.get("b64_json"):
        OUT.write_bytes(base64.b64decode(item["b64_json"]))
    elif item.get("url"):
        image = session.get(item["url"], timeout=(30, 180))
        image.raise_for_status()
        OUT.write_bytes(image.content)
    else:
        raise RuntimeError("No image payload returned")
    print(f"Saved probe image to {OUT.name}", flush=True)


if __name__ == "__main__":
    main()
