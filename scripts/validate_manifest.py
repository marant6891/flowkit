"""Walidacja manifestów Claude Plugin FlowKit (.claude-plugin/plugin.json i marketplace.json).
Sprawdza poprawność JSON, zgodność wersji i istnienie deklarowanych ścieżek.
Uruchom: python scripts/validate_manifest.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_FILE = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_FILE = ROOT / ".claude-plugin" / "marketplace.json"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"

errors = []


def err(msg: str) -> None:
    errors.append(msg)


def validate_plugin_manifest() -> None:
    if not MANIFEST_FILE.exists():
        return err(f"Missing {MANIFEST_FILE}")

    try:
        data = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return err(f"Invalid JSON in plugin.json: {e}")

    for req_field in ["name", "version", "description", "author"]:
        if not data.get(req_field):
            err(f"plugin.json missing required field: '{req_field}'")

    version = data.get("version")
    if version and CHANGELOG_FILE.exists():
        changelog = CHANGELOG_FILE.read_text(encoding="utf-8")
        released = re.search(r"^##\s+\[(\d+\.\d+\.\d+)\]", changelog, re.MULTILINE)
        if not released or released.group(1) != version:
            found = released.group(1) if released else "none"
            err(f"plugin.json version ({version}) does not match latest CHANGELOG.md entry ({found})")

    # Sprawdzenie istnienia ścieżek skills
    for skill in data.get("skills", []):
        path_str = skill.get("path")
        if not path_str:
            err(f"Skill entry missing 'path': {skill}")
        elif not (ROOT / path_str).exists():
            err(f"Declared skill path does not exist: {path_str}")

    # Sprawdzenie istnienia ścieżek agents
    for agent in data.get("agents", []):
        path_str = agent.get("path")
        if not path_str:
            err(f"Agent entry missing 'path': {agent}")
        elif not (ROOT / path_str).exists():
            err(f"Declared agent path does not exist: {path_str}")


def validate_marketplace_manifest() -> None:
    if not MARKETPLACE_FILE.exists():
        return err(f"Missing {MARKETPLACE_FILE}")

    try:
        data = json.loads(MARKETPLACE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return err(f"Invalid JSON in marketplace.json: {e}")

    if not data.get("name"):
        err("marketplace.json missing 'name'")
    if not data.get("plugins") or not isinstance(data["plugins"], list):
        err("marketplace.json missing 'plugins' list")


def main() -> int:
    print("Validating plugin manifests...")
    validate_plugin_manifest()
    validate_marketplace_manifest()

    if errors:
        print(f"Manifest validation failed with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("All manifests validated successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
