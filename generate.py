#!/usr/bin/env python3
"""
generate.py — turns cv.yaml (RenderCV format) + template.html into a dist/ folder.

Run it:   python3 generate.py

cv.yaml is a single source of truth in **RenderCV** format: the same file is
used by `rendercv render cv.yaml` to produce the PDF, and by this script to
produce the website. Here we read the RenderCV schema (cv.name, cv.sections,
...) and map it onto the simple variables that template.html expects.

What it does, step by step:
  1. Read cv.yaml            -> a Python dict (RenderCV schema).
  2. Flatten it              -> a small context dict for the template.
  3. Load template.html      -> a Jinja2 template with {{ placeholders }}.
  4. Render template + data  -> final HTML string.
  5. Write dist/index.html   -> the generated page.
  6. Copy static assets      -> styles.css, matrix.js, main.js, the PDF.

Edit cv.yaml (content), rerun, and both the site and PDF stay in sync.
"""

import re
import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

# Folders/paths are resolved relative to THIS file, so it works from anywhere.
ROOT = Path(__file__).parent
DIST = ROOT / "dist"

# Static files that are copied verbatim (not generated). The PDF is produced by
# `rendercv render cv.yaml`; its name is derived from cv.name below.
STATIC_ASSETS = ["styles.css", "matrix.js", "main.js"]

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def bold(text: str) -> str:
    """Custom Jinja filter: turn markdown **bold** into <b>bold</b> and make
    plain-text arrows (->) render as a nice unicode arrow (→).

    RenderCV highlights use **double asterisks** for emphasis; browsers don't
    understand that, so we convert it to real HTML <b> tags.
    """
    text = text.replace("->", "→")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def format_date(value) -> str:
    """Format a RenderCV date ('YYYY-MM', 'YYYY', or 'present') as 'Mon YYYY'."""
    if value in (None, ""):
        return ""
    s = str(value).strip()
    if s == "present":
        return "present"
    parts = s.split("-")
    year = parts[0]
    if len(parts) >= 2 and parts[1].isdigit():
        month = int(parts[1])
        if 1 <= month <= 12:
            return f"{MONTHS[month - 1]} {year}"
    return year


def format_range(start, end, location) -> str:
    """Build a 'Jun 2025 – present · Tel Aviv' style dates line."""
    start_s = format_date(start)
    end_s = format_date(end)
    span = " – ".join(p for p in (start_s, end_s) if p)
    city = str(location).split(",")[0].strip() if location else ""
    return f"{span} · {city}" if city else span


def flatten(cv: dict) -> dict:
    """Map the RenderCV `cv` block onto the variables template.html expects."""
    sections = cv.get("sections", {}) or {}

    # Contact / social.
    linkedin = ""
    for social in cv.get("social_networks", []) or []:
        if str(social.get("network", "")).lower() == "linkedin":
            linkedin = social.get("username", "")
            break

    # Experience entries -> {role, company, dates, highlights}.
    experience = []
    for job in sections.get("experience", []) or []:
        experience.append({
            "role": job.get("position", ""),
            "company": job.get("company", ""),
            "dates": format_range(job.get("start_date"), job.get("end_date"),
                                  job.get("location")),
            "highlights": job.get("highlights", []) or [],
        })

    # Education entries -> {role, company, dates, highlights}.
    education = []
    for school in sections.get("education", []) or []:
        degree = school.get("degree", "")
        area = school.get("area", "")
        role = ", ".join(p for p in (degree, area) if p)
        education.append({
            "role": role,
            "company": school.get("institution", ""),
            "dates": format_range(school.get("start_date"),
                                  school.get("end_date"),
                                  school.get("location")),
            "highlights": school.get("highlights", []) or [],
        })

    # Skills -> {label, details}. Lowercase labels suit the terminal theme.
    skills = []
    for skill in sections.get("skills", []) or []:
        skills.append({
            "label": str(skill.get("label", "")).lower(),
            "details": skill.get("details", ""),
        })

    # Tagline: RenderCV has no dedicated field, so derive it from the most
    # recent role, e.g. "Software Engineer, Cloud Apps @ Microsoft".
    tagline = ""
    if experience:
        top = experience[0]
        tagline = " @ ".join(p for p in (top["role"], top["company"]) if p)

    name = cv.get("name", "")
    return {
        "name": name,
        "tagline": tagline,
        "location": cv.get("location", ""),
        "email": cv.get("email", ""),
        "phone": cv.get("phone", ""),
        "linkedin": linkedin,
        "summary": " ".join(sections.get("summary", []) or []),
        "experience": experience,
        "education": education,
        "skills": skills,
        "resume_pdf": f"{name.replace(' ', '_')}_CV.pdf",
    }


def main() -> None:
    # 1. Load the RenderCV data and flatten it for the template.
    data = yaml.safe_load((ROOT / "cv.yaml").read_text(encoding="utf-8"))
    context = flatten(data.get("cv", {}) or {})

    # 2. Set up Jinja2 to load templates from this folder.
    env = Environment(
        loader=FileSystemLoader(str(ROOT)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["bold"] = lambda s: Markup(bold(s))

    template = env.get_template("template.html")

    # 3. Render: fill the template with the flattened context.
    html = template.render(**context)

    # 4. Create a clean dist/ folder and write the generated page.
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(html, encoding="utf-8")

    # 5. Copy the static assets next to index.html.
    assets = list(STATIC_ASSETS)
    resume_pdf = context["resume_pdf"]
    if (ROOT / resume_pdf).exists():
        assets.append(resume_pdf)
    else:
        print(f"⚠️  {resume_pdf} not found — run `rendercv render cv.yaml` first "
              f"(the Docker build does this automatically).")
    for asset in assets:
        shutil.copy(ROOT / asset, DIST / asset)

    print(f"✅ Built dist/ ({len(html)} bytes of HTML + {len(assets)} assets)")


if __name__ == "__main__":
    main()
