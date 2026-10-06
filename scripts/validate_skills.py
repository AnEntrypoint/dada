from pathlib import Path
import re
import yaml

root = Path(__file__).resolve().parents[1]
skills = [path for path in (root / "skills").iterdir() if path.is_dir()]
if not skills:
    raise SystemExit("No skill packages found")
for skill in skills:
    entry = skill / "SKILL.md"
    text = entry.read_text(encoding="utf-8")
    sections = text.split("---", 2)
    if len(sections) != 3 or sections[0].strip():
        raise SystemExit(f"{entry}: YAML frontmatter required")
    metadata = yaml.safe_load(sections[1])
    if not isinstance(metadata, dict):
        raise SystemExit(f"{entry}: metadata must be a mapping")
    if metadata.get("name") != skill.name or not re.fullmatch(r"[a-z0-9-]{1,64}", skill.name):
        raise SystemExit(f"{entry}: skill name must match its folder")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        raise SystemExit(f"{entry}: description must contain 1 to 1024 characters")
    ui = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    interface = ui["interface"]
    if not 25 <= len(interface["short_description"]) <= 64:
        raise SystemExit(f"{skill}: short description must contain 25 to 64 characters")
    if "$" + skill.name not in interface["default_prompt"]:
        raise SystemExit(f"{skill}: default prompt must invoke the skill")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if "://" not in target and not target.startswith("#"):
            reference = (skill / target.split("#", 1)[0]).resolve()
            if not reference.is_relative_to(skill.resolve()) or not reference.is_file():
                raise SystemExit(f"{entry}: invalid local reference {target}")
    discovery = root / ".agents" / "skills" / skill.name
    if not discovery.is_symlink() or discovery.resolve() != skill.resolve():
        raise SystemExit(f"{skill}: workspace discovery link is invalid")
    print(f"Valid skill: {skill.name}")
