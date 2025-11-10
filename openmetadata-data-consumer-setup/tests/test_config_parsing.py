import os
import yaml


def load_yaml(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def test_persona_yaml_has_required_fields():
    data = load_yaml('src/config/persona.yaml')
    for field in ['name', 'displayName', 'uiCustomizationName']:
        assert field in data, f"Missing field {field} in persona.yaml"
    assert data['name'] == data['name'].lower().replace(' ', '-'), "Persona name should be slugified (lowercase, hyphens)."


def test_ui_customization_yaml_structure():
    ui = load_yaml('src/config/uiCustomization.yaml')
    assert 'pages' in ui and isinstance(ui['pages'], list) and ui['pages'], 'uiCustomization.yaml must define pages list'
    landing = next((p for p in ui['pages'] if p.get('id') == 'landing'), None)
    assert landing, 'Landing page with id=landing missing'
    assert 'navigation' in ui and isinstance(ui['navigation'], list), 'navigation list missing'


def test_role_yaml_permissions():
    role = load_yaml('src/config/role.yaml')
    perms = role.get('permissions', {})
    assert perms.get('view') is True and perms.get('search') is True, 'Role must allow view & search'
    for deny in ['edit', 'delete']:
        assert perms.get(deny) is False, f"Permission {deny} should be false"


def test_widget_yaml_metrics():
    widget = load_yaml('src/config/widget.yaml')
    w = widget.get('widget', {})
    disp = w.get('displaySettings', {})
    assert disp.get('showMetrics') is True, 'Widget should show metrics'
    assert 'totalProducts' in disp.get('metrics', []), 'Expected totalProducts metric'