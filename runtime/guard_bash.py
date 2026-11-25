"""Hook PreToolUse: agenci FlowKit uruchamiają polecenia wyłącznie przez flowkit_exec.py.

Hook nie wpływa na zwykłe sesje użytkownika ani na innych agentów.
Kod wyjścia 2 blokuje polecenie, a treść ze stderr otrzymuje agent.
"""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flowkit_exec import SENSITIVE_PATH, allow_file, audit_file, check  # noqa: E402

EXECUTOR = Path(__file__).resolve().parent / "flowkit_exec.py"
ROLES = {
    "flowkit-orchestrator": "orchestrator",
    "flowkit-code-analyzer": "analyzer",
    "flowkit-verifier": "verifier",
    "flowkit-implementer": "implementer",
    "flowkit-diagnostics": "diagnostics",
    "flowkit-analyst": "analyst",
    "flowkit-validator": "validator",
}
# Agenci FlowKit bez roli wykonawczej: polecenia są dla nich zablokowane.
NO_EXEC = {"flowkit-planner", "flowkit-product-owner", "flowkit-devops"}
# Nazwy sprzed wersji 1.8.0 (agent-3x3*). Agenci zainstalowani wcześniej nadal są chronieni
# przez nowy runtime. Do usunięcia w kolejnym wydaniu.
LEGACY = {
    "agent-3x3": "flowkit-orchestrator", "agent-3x3-analyzer": "flowkit-code-analyzer",
    "agent-3x3-verifier": "flowkit-verifier", "agent-3x3-implementer": "flowkit-implementer",
    "agent-3x3-diagnostics": "flowkit-diagnostics", "agent-3x3-analyst": "flowkit-analyst",
    "agent-3x3-validator": "flowkit-validator", "agent-3x3-planner": "flowkit-planner",
    "agent-3x3-pm": "flowkit-product-owner", "agent-3x3-devops": "flowkit-devops",
}
PYTHON = {"python", "python3", "py", "python.exe", "python3.exe", "py.exe"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def protected_edit(tool_input: dict) -> str | None:
    """Pliki chronione zmienia tylko użytkownik, także gdy leżą w katalogu z FLOWKIT_EXTRA_PATHS.

    Chronione są: plik zgód, dziennik audytu, runtime FlowKit, katalog `.git` (hooki i konfiguracja gita
    uruchamiają kod) oraz pliki wrażliwe (`.env*` poza `.env.example`, klucze, pliki z sekretami).
    """
    raw = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if not raw:
        return None
    target = resolved(raw)
    if target == allow_file().resolve():
        return "plik zgód użytkownika może zmieniać tylko użytkownik"
    audit_path = audit_file()
    if audit_path is not None and target == audit_path.resolve():
        return "dziennik audytu FlowKit może zmieniać tylko użytkownik"
    if EXECUTOR.parent in target.parents:
        return "pliki runtime FlowKit może zmieniać tylko użytkownik"
    if any(part.lower() == ".git" for part in target.parts):
        return "katalog .git może zmieniać tylko użytkownik (hooki i konfiguracja gita uruchamiają kod)"
    if SENSITIVE_PATH.search(str(target)):
        return f"plik wrażliwy ({target.name}) może zmieniać tylko użytkownik"
    return None


def unsafe_shell_syntax(command: str) -> str | None:
    """Wykrywa łączenie poleceń, przekierowania i podstawienia poza bezpiecznym cudzysłowem."""
    quote = None
    escaped = False
    for char in command:
        if escaped:
            escaped = False
        elif quote == "'":
            quote = None if char == "'" else quote
        elif quote == '"':
            if char == "\\":
                escaped = True
            elif char == '"':
                quote = None
            elif char in "$`":
                return char
        elif char == "\\":
            escaped = True
        elif char in "'\"":
            quote = char
        elif char in ";&|<>`$()\n\r":
            return char
    return "niezamknięty cudzysłów" if quote else None


def resolved(path: str) -> Path:
    path = re.sub(r"^/([a-zA-Z])/", r"\1:/", path)
    return Path(path).expanduser().resolve()


def problem_with(command: str, role: str) -> str | None:
    syntax = unsafe_shell_syntax(command)
    if syntax:
        return f"niedozwolona składnia powłoki: {syntax}"
    try:
        tokens = shlex.split(command.replace("\\", "/"))
    except ValueError as error:
        return str(error)
    if len(tokens) < 6 or tokens[0].rsplit("/", 1)[-1].lower() not in PYTHON:
        return "polecenie musi przejść przez flowkit_exec.py"
    if resolved(tokens[1]) != EXECUTOR or tokens[2:5] != ["--role", role, "--"]:
        return "polecenie musi przejść przez flowkit_exec.py z właściwą rolą"
    return check(role, tokens[5:])


def deny(reason: str, role: str) -> int:
    print(f'FlowKit zablokował polecenie: {reason}. Użyj: python "{EXECUTOR.as_posix()}" --role {role} -- <polecenie>',
          file=sys.stderr)
    return 2


def main() -> int:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        print("FlowKit zablokował polecenie: nieczytelne dane hooka.", file=sys.stderr)
        return 2
    name = str(data.get("agent_type") or "").rsplit(":", 1)[-1]
    name = LEGACY.get(name, name)
    if name not in ROLES and name not in NO_EXEC:
        return 0
    if data.get("tool_name") in EDIT_TOOLS:
        problem = protected_edit(data.get("tool_input") or {})
        if problem:
            print(f"FlowKit zablokował zmianę pliku: {problem}.", file=sys.stderr)
            return 2
        return 0
    role = ROLES.get(name)
    if role is None:
        print(f"FlowKit zablokował polecenie: agent {name} nie może uruchamiać poleceń.", file=sys.stderr)
        return 2
    if data.get("tool_name") != "Bash":
        return 0
    problem = problem_with(str((data.get("tool_input") or {}).get("command") or ""), role)
    return deny(problem, role) if problem else 0


if __name__ == "__main__":
    sys.exit(main())
