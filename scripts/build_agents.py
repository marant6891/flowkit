"""Generuje adaptery agentów z pełnych definicji agents/*_agent.md.

Uruchom po każdej zmianie agenta: python scripts/build_agents.py
Sprawdzenie bez zapisu:            python scripts/build_agents.py --check
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

AGENTS = (
    "agent-3x3", "agent-3x3-analyzer", "agent-3x3-verifier", "agent-3x3-planner",
    "agent-3x3-implementer", "agent-3x3-devops", "agent-3x3-pm",
)

# DevOps celowo nie ma narzędzia Bash: frontmatter jest jedynym twardym ograniczeniem,
# które działa także w agentach instalowanych przez wtyczkę.
CLAUDE_TOOLS = {
    "agent-3x3": ["Read", "Grep", "Glob", "Edit", "Write", "Bash", "Agent", "Skill", "WebFetch", "WebSearch"],
    "agent-3x3-analyzer": ["Read", "Grep", "Glob", "Bash"],
    "agent-3x3-verifier": ["Read", "Grep", "Glob", "Bash"],
    "agent-3x3-planner": ["Read", "Grep", "Glob"],
    "agent-3x3-implementer": ["Read", "Edit", "Write", "Grep", "Glob", "Bash"],
    "agent-3x3-devops": ["Read", "Edit", "Write", "Grep", "Glob", "WebFetch", "WebSearch"],
    "agent-3x3-pm": ["Read", "Grep", "Glob"],
}

CLAUDE_NOTE = """<!-- Plik generowany przez scripts/build_agents.py ze źródła agents/{source}. Nie edytuj ręcznie. -->

## Claude Code tool names

Instructions below use neutral names: `read` = `Read` · `search` = `Grep`, `Glob` · `edit` = `Edit`, `Write` · `execute` = `Bash` · `agent` = `Agent` · `web` = `WebFetch`, `WebSearch`. `ASK_USER` and `WAIT_FOR_APPROVAL` mean: ask in the conversation and stop until the user replies. Use only the tools available to this agent.
"""

VSCODE_NOTE = "<!-- Plik generowany przez scripts/build_agents.py ze źródła agents/{source}. Nie edytuj ręcznie. -->\n"

VSCODE_ORCHESTRATOR_NOTE = """
## VS Code checkpoint (mandatory)

Every `ASK_USER`, `WAIT_FOR_APPROVAL` and end-of-iteration checkpoint ends with a call to `#tool:vscode/askQuestions`. Offer the `Next:` items as up to 3 options, recommended first. Plain-text options do not count as a checkpoint. Subagents never ask the user; they return results to this agent.
"""


def split_source(name: str, root: Path = ROOT) -> tuple[dict, str]:
    text = (root / "agents" / f"{name}_agent.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    _, front, body = text.split("---\n", 2)
    return yaml.safe_load(front), body.lstrip("\n")


def front_matter(data: dict) -> str:
    dumped = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100000)
    return f"---\n{dumped}---\n\n"


def render(name: str, platform: str, root: Path = ROOT) -> str:
    meta, body = split_source(name, root)
    source = f"{name}_agent.md"
    if platform == "claude":
        data = {"name": meta["name"], "description": meta["description"], "tools": CLAUDE_TOOLS[name]}
        return front_matter(data) + CLAUDE_NOTE.format(source=source) + "\n" + body
    note = VSCODE_NOTE.format(source=source)
    if name == "agent-3x3":
        note += VSCODE_ORCHESTRATOR_NOTE
    return front_matter(meta) + note + "\n" + body


def target(name: str, platform: str, root: Path = ROOT) -> Path:
    if platform == "claude":
        return root / "agents" / "adapters" / "claude-code" / f"{name}.md"
    return root / "agents" / "adapters" / "vscode" / f"{name}.agent.md"


def out_of_sync(root: Path = ROOT) -> list[str]:
    stale = []
    for name in AGENTS:
        for platform in ("claude", "vscode"):
            path = target(name, platform, root)
            current = path.read_text(encoding="utf-8").replace("\r\n", "\n") if path.exists() else None
            if current != render(name, platform, root):
                stale.append(str(path.relative_to(root)))
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        stale = out_of_sync()
        for path in stale:
            print(f"Nieaktualny adapter: {path}")
        return 1 if stale else 0
    for name in AGENTS:
        for platform in ("claude", "vscode"):
            target(name, platform).write_text(render(name, platform), encoding="utf-8", newline="\n")
    print(f"Wygenerowano adaptery: {len(AGENTS) * 2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
