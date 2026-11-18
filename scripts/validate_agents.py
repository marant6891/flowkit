"""Walidacja agentów FlowKit: frontmatter, narzędzia, kompletność, synchronizacja i kontrakty.
Uruchom: python scripts/validate_agents.py
"""
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_agents import AGENTS, out_of_sync, target  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

CLAUDE_TOOLS = {
    "Read", "Grep", "Glob", "Edit", "Write", "Bash", "Agent", "Skill", "WebFetch", "WebSearch", "NotebookEdit",
}
VSCODE_TOOLS = {"vscode/askQuestions", "execute", "read", "agent", "edit", "search", "web", "todo"}

# Minimalna treść kontraktów z agents/core, która musi trafić do instalowanych adapterów.
CORE_TERMS = {
    "agent-3x3": ["REPORT_PROGRESS", "ASK_USER", "WAIT_FOR_APPROVAL", "Correction loop", "Reconciliation",
                  "Task profiles", "Risk labels", "Error handling", "SHIP:"],
    "agent-3x3-analyzer": ["Scanned:", "Not checked:", "Confidence:", "Assumptions:"],
    "agent-3x3-verifier": ["Logic", "Contracts", "Tests", "Dependencies", "Security", "Performance",
                           "Consistency", "Docs", "Requirements", "[NOT VERIFIED]"],
    "agent-3x3-planner": ["Iter 1:", "Effort:", "Risks:"],
    "agent-3x3-implementer": ["Self-check", "DONE", "PARTIAL", "BLOCKED"],
    "agent-3x3-devops": ["Validate:", "Apply:", "REQUIRES APPROVAL"],
    "agent-3x3-pm": ["US-1", "AC-1", "Given", "ADR-N"],
}


def parse(path: Path, errors: list[str]) -> tuple[dict | None, str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        errors.append(f"[{path.name}] Missing frontmatter delimiter '---'")
        return None, text
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        errors.append(f"[{path.name}] Invalid frontmatter block")
        return None, text
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as error:
        errors.append(f"[{path.name}] YAML parsing error: {error}")
        return None, text
    if not isinstance(data, dict):
        errors.append(f"[{path.name}] Frontmatter is not a dictionary mapping")
        return None, text
    return data, parts[2]


def check_definition(path: Path, name: str, allowed: set[str], errors: list[str]) -> None:
    data, body = parse(path, errors)
    if data is None:
        return
    if data.get("name") != name:
        errors.append(f"[{path.name}] 'name' must be '{name}', got {data.get('name')!r}")
    if not data.get("description"):
        errors.append(f"[{path.name}] Missing 'description' field in frontmatter")
    tools = data.get("tools")
    if not isinstance(tools, list) or not tools:
        errors.append(f"[{path.name}] 'tools' must be a non-empty list")
        tools = []
    for tool in tools:
        if tool not in allowed:
            errors.append(f"[{path.name}] Unknown tool for this platform: {tool}")
    for term in CORE_TERMS[name]:
        if term not in body:
            errors.append(f"[{path.name}] Missing required contract term: {term}")
    if "vscode_askQuestions" in body:
        errors.append(f"[{path.name}] Use the tool name vscode/askQuestions")
    if name == "agent-3x3" and allowed is VSCODE_TOOLS:
        if "vscode/askQuestions" not in tools or "#tool:vscode/askQuestions" not in body:
            errors.append(f"[{path.name}] VS Code orchestrator must call vscode/askQuestions at checkpoints")
    if name == "agent-3x3-devops" and {"Bash", "execute"} & set(tools):
        errors.append(f"[{path.name}] DevOps agent must not have a command execution tool")


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for name in AGENTS:
        source = root / "agents" / f"{name}_agent.md"
        if not source.exists():
            errors.append(f"[{source.name}] Missing source definition")
            continue
        check_definition(source, name, VSCODE_TOOLS, errors)
        for platform, allowed in (("claude", CLAUDE_TOOLS), ("vscode", VSCODE_TOOLS)):
            path = target(name, platform, root)
            if not path.exists():
                errors.append(f"[{path.name}] Missing {platform} adapter")
                continue
            check_definition(path, name, allowed, errors)
        core_name = re.sub(r"^agent-3x3-?", "", name) or "orchestrator"
        if not (root / "agents" / "core" / f"{core_name}.md").exists():
            errors.append(f"[{core_name}.md] Missing core contract")
    if not errors:
        errors.extend(f"[{path}] Adapter is out of sync: run python scripts/build_agents.py" for path in out_of_sync(root))
    return errors


def main() -> int:
    print("Validating agent files...")
    errors = validate()
    if errors:
        print(f"Agent validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"All {len(AGENTS)} agents validated across source and 2 platform adapters!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
