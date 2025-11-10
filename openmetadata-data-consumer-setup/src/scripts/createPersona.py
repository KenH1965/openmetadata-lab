import os
import json
import yaml
import sys
import requests


UI_CUSTOMIZATION_NAME_KEY = "uiCustomizationName"


def load_persona_config(path: str) -> dict:
    with open(path, "r") as f:
        if path.endswith(".yaml") or path.endswith(".yml"):
            return yaml.safe_load(f)
        return json.load(f)


def require_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        print(f"ERROR: Environment variable {var} is required.")
        sys.exit(1)
    return value


def get_ui_customization_id(base_url: str, token: str, name: str) -> str:
    url = f"{base_url}/api/v1/system/ui/customization/name/{name}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        data = resp.json()
        return data.get("id")
    print(f"ERROR: Failed to fetch uiCustomization '{name}': {resp.status_code} {resp.text}")
    sys.exit(1)


def persona_exists(base_url: str, token: str, name: str) -> dict | None:
    url = f"{base_url}/api/v1/personas/name/{name}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        return resp.json()
    return None


def create_persona(base_url: str, token: str, payload: dict) -> dict:
    url = f"{base_url}/api/v1/personas"
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=payload)
    if resp.status_code in (200, 201):
        return resp.json()
    # If already exists, return existing object (idempotence by name)
    if resp.status_code == 409:
        existing = persona_exists(base_url, token, payload["name"])
        if existing:
            return existing
    print(f"ERROR: Persona creation failed: {resp.status_code} {resp.text}")
    sys.exit(1)


def build_persona_payload(config: dict, ui_customization_id: str) -> dict:
    name_slug = config.get("name") or "data-consumer"
    display_name = config.get("displayName", "Data Consumer")
    description = config.get("description", "Business/data consumer persona focusing on search & data product discovery.")
    default_flag = config.get("default", False)
    header_color = config.get("headerColor", "#0F62FE")
    preferences = {
        "personaName": display_name,
        "landingPageSettings": {"headerColor": header_color}
    }
    return {
        "name": name_slug,
        "displayName": display_name,
        "description": description,
        "uiCustomization": {"id": ui_customization_id, "type": "uiCustomization"},
        "default": default_flag,
        "personaPreferences": [preferences]
    }


def main():
    om_url = require_env("OM_URL")
    om_token = require_env("OM_TOKEN")
    config_path = "src/config/persona.yaml"
    persona_config = load_persona_config(config_path)

    ui_customization_name = persona_config.get(UI_CUSTOMIZATION_NAME_KEY, "data-consumer-ui")
    ui_customization_id = get_ui_customization_id(om_url, om_token, ui_customization_name)

    existing = persona_exists(om_url, om_token, persona_config.get("name", "data-consumer"))
    if existing:
        print(f"Persona '{existing.get('name')}' already exists (id: {existing.get('id')}). Skipping creation.")
        return

    payload = build_persona_payload(persona_config, ui_customization_id)
    created = create_persona(om_url, om_token, payload)
    print(f"Created persona '{created.get('name')}' (id: {created.get('id')}).")


if __name__ == "__main__":
    main()