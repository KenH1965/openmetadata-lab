# Open Metadata Data Consumer Setup

Provisionerar en Data Consumer-upplevelse i OpenMetadata (≥1.9):

- UI Customization (landing page + navigation)
- Persona kopplad till UI:t
- Read/Search Policy & Roll
- Data Products widget-konfiguration

## Innehåll

| Del                                     | Syfte                                                             |
| --------------------------------------- | ----------------------------------------------------------------- |
| `src/config/*.yaml`                     | Deklarativ konfiguration (persona, uiCustomization, role, widget) |
| `src/scripts/createUICustomization.py`  | Skapar UI Customization via API                                   |
| `src/scripts/createPersona.py`          | Skapar Persona och kopplar UI                                     |
| `src/scripts/createDataConsumerRole.py` | Skapar policy + roll (read/search)                                |
| `src/scripts/addWidgetToUI.py`          | Uppdaterar lokal widget.yaml (framtida integration)               |
| `tests/test_config_parsing.py`          | Grundtester för YAML-struktur                                     |

## Förutsättningar

1. Python 3.12+ och virtuellt venv rekommenderas.
2. Ett OpenMetadata-token med rätt att skapa systemobjekt.
3. Miljövariabler enligt nedan.

## Miljövariabler

```bash
export OM_URL=http://127.0.0.1:8585
export OM_TOKEN=eyJraWQi...
export CURL_TIMEOUT=20
export CURL_RETRIES=2
export CURL_INSECURE=0   # 1 för att inaktivera TLS verify (ej prod)
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Körordning

```bash
python src/scripts/createUICustomization.py
python src/scripts/createPersona.py
python src/scripts/createDataConsumerRole.py
```

## Snabbvalidering

```bash
pytest -q
```

## Konfigurationsfiler

- `persona.yaml`: namn, displayName, uiCustomizationName, headerColor.
- `uiCustomization.yaml`: pages + navigation + panels.
- `role.yaml`: deklarativ permissions (informativ) + policyregler.
- `widget.yaml`: layout och datakällor (lokal modell; kräver koppling i OM UI).

## Policy & Roll

Policy skapas med tre regler:

- AllowViewAll (allow)
- AllowSearchAll (allow)
- DenyWrites (deny allt utanför view/search)

Roll refererar policyn och blir läs-/sök-roll för Data Consumers.

## Tilldelning till användare (exempel)

```bash
USER_ID=<uuid>
ROLE_ID=$(curl -s "$OM_URL/api/v1/roles/name/role_data_consumer" -H "Authorization: Bearer $OM_TOKEN" | jq -r '.id')
PERSONA_ID=$(curl -s "$OM_URL/api/v1/personas/name/data-consumer" -H "Authorization: Bearer $OM_TOKEN" | jq -r '.id')

curl -s -X PATCH "$OM_URL/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $OM_TOKEN" \
  -H "Content-Type: application/json-patch+json" \
  -d "[ {\"op\":\"add\", \"path\":\"/roles/0\", \"value\": {\"id\":\"$ROLE_ID\", \"type\":\"role\"} } ]"

curl -s -X PATCH "$OM_URL/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $OM_TOKEN" \
  -H "Content-Type: application/json-patch+json" \
  -d "[ {\"op\":\"add\", \"path\":\"/personas/0\", \"value\": {\"id\":\"$PERSONA_ID\", \"type\":\"persona\"} } ]"
```

## Vanliga problem

| Problem          | Lösning                                 |
| ---------------- | --------------------------------------- |
| 401 Unauthorized | Kontrollera OM_TOKEN                    |
| 409 Conflict     | Objekt finns redan → skript hoppar över |
| SSL/TLS fel      | Sätt `CURL_INSECURE=1` (ej prod)        |
| Timeout          | Öka `CURL_TIMEOUT`                      |

## Nästa förbättringar

- Mockade tester (requests-mock)
- Script för user assignment via email lookup
- Health-check före provisioning

## Licens

MIT License – se `LICENSE`.
