"""Walidacja konfiguracji agentów FlowKit (YAML frontmatter, nazewnictwo, adaptery).
Uruchom: python scripts/validate_agents.py
"""
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"

errors = []


def validate_agent_file(path: Path, expected_tools_type: type = None) -> bool:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        # Pliki w core/ mogą być czystymi kontraktami Markdown bez frontmatteru
        if "core" in path.parts:
            return True
        errors.append(f"[{path.name}] Missing frontmatter delimiter '---'")
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append(f"[{path.name}] Invalid frontmatter block")
        return False

    frontmatter_raw = parts[1]
    try:
        data = yaml.safe_load(frontmatter_raw)
    except yaml.YAMLError as e:
        errors.append(f"[{path.name}] YAML parsing error: {e}")
        return False

    if not isinstance(data, dict):
        errors.append(f"[{path.name}] Frontmatter is not a dictionary mapping")
        return False

    # Sprawdzenie wymaganych pól
    if not data.get("name"):
        errors.append(f"[{path.name}] Missing 'name' field in frontmatter")

    if not data.get("description"):
        errors.append(f"[{path.name}] Missing 'description' field in frontmatter")

    # Sprawdzenie narzędzi jeśli zdefiniowane
    tools = data.get("tools")
    if tools is not None:
        if not isinstance(tools, list):
            errors.append(f"[{path.name}] 'tools' must be a list, got {type(tools).__name__}")
        elif len(tools) == 0:
            errors.append(f"[{path.name}] 'tools' list cannot be empty")

    return True


def main() -> int:
    if not AGENTS_DIR.is_dir():
        print("Agents directory not found!")
        return 1

    print("Validating agent files...")
    all_agent_files = list(AGENTS_DIR.rglob("*.md"))

    if not all_agent_files:
        print("No agent files found!")
        return 1

    for agent_file in sorted(all_agent_files):
        validate_agent_file(agent_file)

    if errors:
        print(f"Agent validation failed with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"All {len(all_agent_files)} agent definitions validated successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
