import sys, re
from pathlib import Path
import yaml

skills_dir = Path("skills")
errors = []

for skill_path in sorted(skills_dir.iterdir()):
    if not skill_path.is_dir() or skill_path.name.startswith("_"):
        continue
    skill_name = skill_path.name
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        errors.append(f"[{skill_name}] Missing SKILL.md"); continue
    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        errors.append(f"[{skill_name}] No YAML frontmatter"); continue
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append(f"[{skill_name}] Incomplete frontmatter"); continue
    try:
        meta = yaml.safe_load(parts[1])
    except Exception as e:
        errors.append(f"[{skill_name}] YAML error: {e}"); continue
    if not isinstance(meta, dict):
        errors.append(f"[{skill_name}] Not a dict"); continue
    if not meta.get("name"):
        errors.append(f"[{skill_name}] Missing name")
    elif meta["name"] != skill_name:
        errors.append(f"[{skill_name}] name mismatch: frontmatter={meta['name']} dir={skill_name}")
    if not meta.get("description"):
        errors.append(f"[{skill_name}] Missing description")
    if not meta.get("version"):
        errors.append(f"[{skill_name}] Missing version")
    tags = meta.get("tags")
    if not tags or not isinstance(tags, list) or len(tags) == 0:
        errors.append(f"[{skill_name}] Missing or empty tags")
    if not (skill_path / "templates").is_dir():
        errors.append(f"[{skill_name}] Missing templates/")
    link_pattern = re.compile(r"\[.*?\]\(\./([^)]+)\)")
    for match in link_pattern.finditer(parts[2]):
        relative = match.group(1)
        target = skill_path / relative
        if not target.exists():
            errors.append(f"[{skill_name}] Broken link: ./{relative}")

if errors:
    print(f"FAIL - {len(errors)} errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print("All skills OK!")
