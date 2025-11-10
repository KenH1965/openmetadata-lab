import os
import json
import yaml
import sys
import requests


def require_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        print(f"ERROR: Environment variable {var} is required.")
        sys.exit(1)
    return value


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        if path.endswith(".yaml") or path.endswith(".yml"):
            return yaml.safe_load(f)
        return json.load(f)


def get_ui_customization(base_url: str, token: str, name: str) -> dict | None:
    url = f"{base_url}/api/v1/system/ui/customization/name/{name}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        return resp.json()
    return None


def create_ui_customization(base_url: str, token: str, payload: dict) -> dict:
    url = f"{base_url}/api/v1/system/ui/customization"
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=payload)
    if resp.status_code in (200, 201):
        return resp.json()
    if resp.status_code == 409:
        existing = get_ui_customization(base_url, token, payload.get("name"))
        if existing:
            return existing
    print(f"ERROR: UI customization creation failed: {resp.status_code} {resp.text}")
    sys.exit(1)


def main():
    om_url = require_env("OM_URL")
    om_token = require_env("OM_TOKEN")
    config_path = "src/config/uiCustomization.yaml"
    cfg = load_config(config_path)

    name = cfg.get("name")
    if not name:
        print("ERROR: uiCustomization.json must contain 'name'.")
        sys.exit(1)

    existing = get_ui_customization(om_url, om_token, name)
    if existing:
        print(f"UI Customization '{name}' already exists (id: {existing.get('id')}). Skipping creation.")
        return

    created = create_ui_customization(om_url, om_token, cfg)
    print(f"Created UI Customization '{created.get('name')}' (id: {created.get('id')}).")


if __name__ == "__main__":
    main()