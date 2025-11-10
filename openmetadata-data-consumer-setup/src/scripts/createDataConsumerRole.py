import os
import sys
import time
import json
import yaml
import requests


POLICY_NAME = "policy_data_consumer_readonly"
ROLE_NAME = "role_data_consumer"
ROLE_DISPLAY_NAME = "Data Consumer"


def env(name: str, default=None):
    val = os.getenv(name, default)
    if val is None:
        print(f"ERROR: Missing env var {name}")
        sys.exit(1)
    return val


def request_with_retry(method: str, url: str, token: str, **kwargs):
    retries = int(os.getenv("CURL_RETRIES", "2"))
    timeout = int(os.getenv("CURL_TIMEOUT", "20"))
    verify = not bool(int(os.getenv("CURL_INSECURE", "0")))
    headers = kwargs.pop("headers", {})
    headers.setdefault("Authorization", f"Bearer {token}")
    if method in ("post", "patch", "put"):
        headers.setdefault("Content-Type", "application/json")
    last_exc = None
    for attempt in range(1, retries + 2):
        try:
            resp = requests.request(method, url, headers=headers, timeout=timeout, verify=verify, **kwargs)
            return resp
        except requests.RequestException as e:
            last_exc = e
            print(f"WARN: Request failure attempt {attempt}/{retries+1}: {e}")
            time.sleep(1)
    print(f"ERROR: Exhausted retries for {url}: {last_exc}")
    sys.exit(1)


def get_policy(base_url: str, token: str, name: str):
    url = f"{base_url}/api/v1/policies/name/{name}"
    resp = request_with_retry("get", url, token)
    if resp.status_code == 200:
        return resp.json()
    return None


def create_policy(base_url: str, token: str):
    existing = get_policy(base_url, token, POLICY_NAME)
    if existing:
        print(f"Policy '{POLICY_NAME}' exists (id: {existing.get('id')}).")
        return existing
    url = f"{base_url}/api/v1/policies"
    payload = {
        "name": POLICY_NAME,
        "displayName": "Data Consumer ReadOnly",
        "rules": [
            {"name": "AllowViewAll", "resources": ["All"], "operations": ["ViewAll"], "effect": "allow"},
            {"name": "AllowSearchAll", "resources": ["All"], "operations": ["SearchAll"], "effect": "allow"},
            {
                "name": "DenyWrites",
                "resources": ["All"],
                "operations": ["All"],
                "effect": "deny",
                "condition": "operation not in ['ViewAll','SearchAll']"
            }
        ],
        "enabled": True
    }
    resp = request_with_retry("post", url, token, json=payload)
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"Created policy '{POLICY_NAME}' (id: {data.get('id')}).")
        return data
    if resp.status_code == 409:  # Conflict; fetch existing
        existing = get_policy(base_url, token, POLICY_NAME)
        if existing:
            return existing
    print(f"ERROR: Policy creation failed {resp.status_code}: {resp.text}")
    sys.exit(1)


def get_role(base_url: str, token: str, name: str):
    url = f"{base_url}/api/v1/roles/name/{name}"
    resp = request_with_retry("get", url, token)
    if resp.status_code == 200:
        return resp.json()
    return None


def create_role(base_url: str, token: str, policy_id: str):
    existing = get_role(base_url, token, ROLE_NAME)
    if existing:
        print(f"Role '{ROLE_NAME}' exists (id: {existing.get('id')}).")
        return existing
    url = f"{base_url}/api/v1/roles"
    payload = {
        "name": ROLE_NAME,
        "displayName": ROLE_DISPLAY_NAME,
        "policies": [{"id": policy_id, "type": "policy"}],
        "description": "Read/search-only role for data consumers"
    }
    resp = request_with_retry("post", url, token, json=payload)
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"Created role '{ROLE_NAME}' (id: {data.get('id')}).")
        return data
    if resp.status_code == 409:
        existing = get_role(base_url, token, ROLE_NAME)
        if existing:
            return existing
    print(f"ERROR: Role creation failed {resp.status_code}: {resp.text}")
    sys.exit(1)


def main():
    base_url = env("OM_URL")
    token = env("OM_TOKEN")
    # role.yaml can later hold additional metadata; we load it for possible extensions
    role_cfg_path = "src/config/role.yaml"
    if os.path.exists(role_cfg_path):
        with open(role_cfg_path, "r") as f:
            try:
                role_cfg = yaml.safe_load(f)
            except Exception as e:
                print(f"WARN: Failed to parse role.yaml: {e}")
                role_cfg = {}
    else:
        role_cfg = {}

    policy = create_policy(base_url, token)
    create_role(base_url, token, policy.get("id"))


if __name__ == "__main__":
    main()