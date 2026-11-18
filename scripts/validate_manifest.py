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

    # Claude Code akceptuje tu ścieżkę albo listę ścieżek zaczynających się od "./".
    for key, suffix in (("skills", ""), ("agents", ".md")):
        entries = data.get(key, [])
        entries = [entries] if isinstance(entries, str) else entries
        if not isinstance(entries, list):
            err(f"plugin.json '{key}' must be a path or a list of paths")
            continue
        for entry in entries:
            if not isinstance(entry, str) or not entry.startswith("./"):
                err(f"plugin.json '{key}' entry must be a path starting with './': {entry!r}")
            elif not entry.endswith(suffix):
                err(f"plugin.json '{key}' entry must end with '{suffix}': {entry}")
            elif not (ROOT / entry).exists():
                err(f"Declared {key} path does not exist: {entry}")

    # Domyślne skanowanie skills/ nie może wykryć szablonu jako skilla.
    if (ROOT / "skills" / "_template" / "SKILL.md").exists():
        err("skills/_template must use SKILL.template.md, otherwise the plugin loads it as a skill")


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
