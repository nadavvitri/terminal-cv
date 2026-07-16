#!/usr/bin/env python3
"""
generate.py — turns cv.yaml + template.html into a ready-to-serve dist/ folder.

Run it:   python3 generate.py

What it does, step by step:
  1. Read cv.yaml            -> a Python dict of your CV data.
  2. Load template.html      -> a Jinja2 template with {{ placeholders }}.
  3. Render template + data  -> final HTML string.
  4. Write dist/index.html   -> the generated page.
  5. Copy static assets      -> styles.css, matrix.js, main.js, the PDF.

The result: a self-contained dist/ folder that Nginx can serve as-is.
Edit cv.yaml (content) or template.html (structure), rerun, and dist/ updates.
"""

import re
import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Folders/paths are resolved relative to THIS file, so it works from anywhere.
ROOT = Path(__file__).parent
DIST = ROOT / "dist"

# Static files that are copied verbatim (not generated).
STATIC_ASSETS = ["styles.css", "matrix.js", "main.js", "Nadav_Vitri_CV.pdf"]


def bold(text: str) -> str:
    """Custom Jinja filter: turn markdown **bold** into <b>bold</b>.

    Our cv.yaml highlights use **double asterisks** for emphasis (like in the
    original RenderCV file). Browsers don't understand that, so we convert it
    to real HTML <b> tags. The regex finds **...** and replaces the wrapper.
    """
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def main() -> None:
    # 1. Load the data from YAML into a Python dictionary.
    data = yaml.safe_load((ROOT / "cv.yaml").read_text(encoding="utf-8"))

    # 2. Set up Jinja2 to load templates from this folder.
    #    autoescape protects against broken HTML, but we mark the bold filter
    #    output as safe below so our <b> tags survive.
    env = Environment(
        loader=FileSystemLoader(str(ROOT)),
        autoescape=select_autoescape(["html"]),
    )
    # Register our custom filter, wrapping its output as "safe" HTML.
    from markupsafe import Markup
    env.filters["bold"] = lambda s: Markup(bold(s))

    template = env.get_template("template.html")

    # 3. Render: fill the template with the data dict (**data spreads keys).
    html = template.render(**data)

    # 4. Create a clean dist/ folder and write the generated page.
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(html, encoding="utf-8")

    # 5. Copy the static assets next to index.html.
    for asset in STATIC_ASSETS:
        shutil.copy(ROOT / asset, DIST / asset)

    print(f"✅ Built dist/ ({len(html)} bytes of HTML + {len(STATIC_ASSETS)} assets)")


if __name__ == "__main__":
    main()
