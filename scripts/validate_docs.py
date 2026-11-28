"""Sprawdza, czy README i dokumentacja nadążają za kodem FlowKit. Uruchom: python scripts/validate_docs.py

Źródłem prawdy są definicje (manifest wtyczki, agenci, skille). Dokumentacja musi wymieniać to, co one zawierają:
- wersja w README = wersja w .claude-plugin/plugin.json,
- każdy prefiks orkiestratora jest w README, docs/USAGE.md i .github/copilot-instructions.md,
- każdy tryb audytu Verifiera (`*-AUDIT:`) jest w README,
- każdy subagent jest w tabeli README i w instrukcjach Copilota, a liczba subagentów w README się zgadza,
- każdy skill ma regułę w instrukcjach Copilota i rozdział w docs/USAGE.md,
- względne linki w README, docs/USAGE.md, CONTRIBUTING.md i DEVELOPMENT.md prowadzą do istniejących plików.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_agents  # noqa: E402

DOCS = {
    "README.md": ROOT / "README.md",
    "docs/USAGE.md": ROOT / "docs" / "USAGE.md",
    ".github/copilot-instructions.md": ROOT / ".github" / "copilot-instructions.md",
}
LINKED = ["README.md", "docs/USAGE.md", "CONTRIBUTING.md", "DEVELOPMENT.md"]
LINK = re.compile(r"\]\(([^)\s]+)\)")
PREFIX = re.compile(r"`([A-Z][A-Z-]*:)`")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def orchestrator_prefixes() -> list[str]:
    """Prefiksy z tabeli „## Prefixes” w definicji orkiestratora (pierwsza kolumna)."""
    text = read(ROOT / "agents" / "flowkit-orchestrator_agent.md")
    section = text.split("## Prefixes", 1)[1].split("\n## ", 1)[0]
    prefixes = []
    for line in section.splitlines():
        if line.startswith("| `"):
            prefixes += PREFIX.findall(line.split("|")[1])
    return prefixes


def audit_modes() -> list[str]:
    text = read(ROOT / "agents" / "flowkit-verifier_agent.md")
    return sorted(set(re.findall(r"`([A-Z]+-AUDIT:)`", text)))


def skills() -> list[str]:
    return sorted(p.name for p in (ROOT / "skills").glob("flowkit-*") if (p / "SKILL.md").exists())


def check() -> list[str]:
    errors: list[str] = []
    docs = {name: read(path) for name, path in DOCS.items()}
    readme, usage, copilot = docs["README.md"], docs["docs/USAGE.md"], docs[".github/copilot-instructions.md"]

    version = json.loads(read(ROOT / ".claude-plugin" / "plugin.json"))["version"]
    found = re.search(r"Wersja: \*\*([\d.]+)\*\*", readme)
    if not found or found.group(1) != version:
        errors.append(f"README.md: wersja {found.group(1) if found else 'brak'} różni się od plugin.json ({version})")

    prefixes = orchestrator_prefixes()
    if not prefixes:
        errors.append("agents/flowkit-orchestrator_agent.md: nie znaleziono tabeli „## Prefixes”")
    for prefix in prefixes:
        for name, text in docs.items():
            if f"`{prefix}`" not in text and f"{prefix} " not in text:
                errors.append(f"{name}: brak prefiksu orkiestratora `{prefix}`")

    for mode in audit_modes():
        if f"`{mode}`" not in readme:
            errors.append(f"README.md: brak trybu Verifiera `{mode}`")

    subagents = [a for a in build_agents.AGENTS if a != build_agents.ORCHESTRATOR]
    for agent in subagents:
        if f"**{agent}**" not in readme:
            errors.append(f"README.md: brak subagenta {agent} w tabeli „Subagenci”")
        if f"`{agent}`" not in copilot:
            errors.append(f".github/copilot-instructions.md: brak subagenta {agent}")
    count = re.search(r"do (\d+) subagentów", readme)
    if count and int(count.group(1)) != len(subagents):
        errors.append(f"README.md: „do {count.group(1)} subagentów”, a jest ich {len(subagents)}")

    for skill in skills():
        if f"`{skill}`" not in copilot:
            errors.append(f".github/copilot-instructions.md: brak reguły aktywacji skilla {skill}")
        if not re.search(rf"^#+ .*`{re.escape(skill)}`", usage, re.MULTILINE):
            errors.append(f"docs/USAGE.md: brak rozdziału dla skilla {skill}")

    for name in LINKED:
        path = ROOT / name
        for link in LINK.findall(read(path)):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = link.split("#", 1)[0]
            if target.startswith("../../"):  # odnośniki GitHub (issues, discussions) względem repozytorium
                continue
            if target and not (path.parent / target).exists():
                errors.append(f"{name}: martwy link {link}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print(f"Dokumentacja nieaktualna ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Dokumentacja zgodna z agentami, skillami i manifestem.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
