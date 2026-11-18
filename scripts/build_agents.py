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
    "agent-3x3-implementer", "agent-3x3-devops", "agent-3x3-pm", "agent-3x3-diagnostics", "agent-3x3-analyst",
)

# Listy narzędzi są jawne: agenci działają lokalnie, bez narzędzi webowych i bez MCP.
CLAUDE_TOOLS = {
    "agent-3x3": ["Read", "Grep", "Glob", "Edit", "Write", "Bash", "Agent", "Skill"],
    "agent-3x3-analyzer": ["Read", "Grep", "Glob", "Bash"],
    "agent-3x3-verifier": ["Read", "Grep", "Glob", "Bash"],
    "agent-3x3-planner": ["Read", "Grep", "Glob"],
    "agent-3x3-implementer": ["Read", "Edit", "Write", "Grep", "Glob", "Bash"],
    "agent-3x3-devops": ["Read", "Edit", "Write", "Grep", "Glob"],
    "agent-3x3-pm": ["Read", "Grep", "Glob"],
    "agent-3x3-diagnostics": ["Read", "Grep", "Glob", "Bash"],
    "agent-3x3-analyst": ["Read", "Grep", "Glob", "Edit", "Write", "Bash", "Skill"],
}

# Orkiestrator dziedziczy model sesji; subagenci mają jawny model i limit kroków.
CLAUDE_LIMITS = {
    "agent-3x3-analyzer": ("sonnet", 15),
    "agent-3x3-verifier": ("sonnet", 20),
    "agent-3x3-planner": ("sonnet", 12),
    "agent-3x3-implementer": ("sonnet", 25),
    "agent-3x3-devops": ("sonnet", 15),
    "agent-3x3-pm": ("sonnet", 10),
    "agent-3x3-diagnostics": ("sonnet", 15),
    "agent-3x3-analyst": ("sonnet", 40),
}

EXEC_ROLES = {
    "agent-3x3": "orchestrator",
    "agent-3x3-analyzer": "analyzer",
    "agent-3x3-verifier": "verifier",
    "agent-3x3-implementer": "implementer",
    "agent-3x3-diagnostics": "diagnostics",
    "agent-3x3-analyst": "analyst",
}

GUARD_HOOK = {"PreToolUse": [{"matcher": "Bash", "hooks": [{
    "type": "command",
    "command": 'python "$HOME/.claude/flowkit/runtime/guard_bash.py"',
    "onFailure": "block",
}]}]}

GENERATED = "<!-- Plik generowany przez scripts/build_agents.py ze źródła agents/SOURCE. Nie edytuj ręcznie. -->\n"

CLAUDE_NOTE = """
## Claude Code tool names

Instructions below use neutral names: `read` = `Read` · `search` = `Grep`, `Glob` · `edit` = `Edit`, `Write` · `execute` = `Bash` · `agent` = `Agent`. `ASK_USER` and `WAIT_FOR_APPROVAL` mean: ask in the conversation and stop until the user replies. Use only the tools available to this agent.
"""

EXEC_NOTE = """
## Local command execution

Run every command only through the local executor: `python "<runtime>/flowkit_exec.py" --role ROLE -- <command> [args]`. Do not use pipes, redirects or command chaining. `<runtime>` is RUNTIME. Rejected commands are outside this agent's role: report them instead of working around the rule. Documents: `read-document <file> [--outline] [--lines FROM-TO]`.
"""

CLAUDE_RUNTIME = "`${CLAUDE_PLUGIN_ROOT}/runtime` in a plugin install, otherwise `~/.claude/flowkit/runtime`"
VSCODE_RUNTIME = "`.github/flowkit/runtime` in the workspace"

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


def exec_note(name: str, runtime: str) -> str:
    role = EXEC_ROLES.get(name)
    return EXEC_NOTE.replace("ROLE", role).replace("RUNTIME", runtime) if role else ""


def render(name: str, platform: str, root: Path = ROOT) -> str:
    meta, body = split_source(name, root)
    note = GENERATED.replace("SOURCE", f"{name}_agent.md")
    if platform == "claude":
        data = {"name": meta["name"], "description": meta["description"], "tools": CLAUDE_TOOLS[name]}
        if name in CLAUDE_LIMITS:
            data["model"], data["maxTurns"] = CLAUDE_LIMITS[name]
        if name in EXEC_ROLES:
            data["hooks"] = GUARD_HOOK
        return front_matter(data) + note + CLAUDE_NOTE + exec_note(name, CLAUDE_RUNTIME) + "\n" + body
    if name == "agent-3x3":
        note += VSCODE_ORCHESTRATOR_NOTE
    return front_matter(meta) + note + exec_note(name, VSCODE_RUNTIME) + "\n" + body


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
