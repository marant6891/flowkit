"""Walidacja struktury skilli FlowKit. Uruchom: python scripts/validate_skills.py"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VERSION = re.compile(r"^\d+\.\d+$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
EXTERNAL = ("http://", "https://", "mailto:", "#")

errors = []


def has_md(directory: Path) -> bool:
    return directory.is_dir() and any(directory.glob("*.md"))


def check_skill(skill_path: Path, readme: str) -> None:
    name = skill_path.name

    def err(msg: str) -> None:
        errors.append(f"[{name}] {msg}")

    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        return err("Missing SKILL.md")
    content = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", content, re.DOTALL)
    if not match:
        return err("SKILL.md must start with a YAML frontmatter block delimited by '---' lines")
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        return err(f"YAML parsing error: {e}")
    if not isinstance(meta, dict):
        return err("Frontmatter is not a YAML mapping")
    body = match.group(2)

    # Frontmatter
    if not KEBAB.match(name):
        err("Directory name is not kebab-case (lowercase letters, digits, hyphens)")
    if not meta.get("name"):
        err("Missing 'name' in frontmatter")
    elif meta["name"] != name:
        err(f"'name' in frontmatter ('{meta['name']}') does not match directory name")
    if not meta.get("description"):
        err("Missing 'description' in frontmatter")
    version = meta.get("version")
    if version is None:
        err("Missing 'version' in frontmatter (e.g. version: \"1.0\")")
    elif not isinstance(version, str) or not VERSION.match(version):
        err(f"'version' must be a quoted string in X.Y format, got {version!r}")
        version = None
    tags = meta.get("tags")
    if not isinstance(tags, list) or len(tags) < 3:
        err("'tags' must be a list with at least 3 entries")

    # Prosty język: każdy skill odwołuje się do wspólnego standardu (runtime/procedures/plain-language.md).
    if "procedures/plain-language.md" not in body:
        err("SKILL.md must reference the plain language standard `<runtime>/procedures/plain-language.md`")
    checklists = " ".join(p.read_text(encoding="utf-8") for p in (skill_path / "checklists").glob("*.md"))
    if "prost" not in checklists.casefold():
        err("checklists/ must include a plain language check (prosty język)")

    # Wymagana struktura
    if not has_md(skill_path / "templates"):
        err("'templates/' must contain at least one .md file")
    if not has_md(skill_path / "checklists"):
        err("'checklists/' must contain at least one .md file")
    changelog = skill_path / "CHANGELOG.md"
    if not changelog.exists():
        err("Missing CHANGELOG.md")
    elif version:
        latest = re.search(r"^##\s+\[?(\d+\.\d+)", changelog.read_text(encoding="utf-8"), re.MULTILINE)
        if not latest or latest.group(1) != version:
            found = latest.group(1) if latest else "none"
            err(f"Latest CHANGELOG.md entry ({found}) does not match frontmatter version ({version})")

    # Linki względne w SKILL.md + odwołanie do checklisty weryfikacji
    has_checklist_ref = False
    for link in LINK.findall(body):
        if link.startswith(EXTERNAL):
            continue
        clean = link.split("#", 1)[0]
        if clean.startswith(("checklists/", "./checklists/")):
            has_checklist_ref = True
        target = skill_path / clean
        if not target.exists():
            err(f"Broken link in SKILL.md: {link}")
    if not has_checklist_ref:
        err("SKILL.md must reference at least one checklist file in checklists/")
    # Jedno zachowanie pytań we wszystkich skillach: okno pytań i wiersz diagnostyczny `Ask:`.
    if not re.search(r"^# Pytania do użytkownika\s*$", body, re.MULTILINE) or "Ask: window" not in body:
        err("SKILL.md must contain the '# Pytania do użytkownika' section with the 'Ask:' diagnostic line")

    # Katalog w README
    row = re.search(rf"^\|\s*\*\*{re.escape(name)}\*\*\s*\|\s*`([^`]+)`", readme, re.MULTILINE)
    if not row:
        err("Skill is not listed in the README.md catalog table")
    elif version and row.group(1) != version:
        err(f"README.md lists version {row.group(1)}, frontmatter has {version}")


def check_release() -> None:
    manifest = ROOT / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        errors.append("[repo] Missing .claude-plugin/plugin.json")
        return
    try:
        plugin_version = json.loads(manifest.read_text(encoding="utf-8")).get("version")
    except json.JSONDecodeError as e:
        errors.append(f"[repo] .claude-plugin/plugin.json is not valid JSON: {e}")
        return
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    released = re.search(r"^##\s+\[(\d+\.\d+\.\d+)\]", changelog, re.MULTILINE)
    if not released or released.group(1) != plugin_version:
        found = released.group(1) if released else "none"
        errors.append(
            f"[repo] plugin.json version ({plugin_version}) does not match "
            f"latest released CHANGELOG.md entry ({found})"
        )


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print("Skills directory not found!")
        return 1
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for skill_path in sorted(SKILLS_DIR.iterdir()):
        if skill_path.is_dir() and not skill_path.name.startswith("_"):
            check_skill(skill_path, readme)
    check_release()
    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All skills validated successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
