from pathlib import Path

# --- Configuration ---
DOCS_FOLDER = "docs"
MKDOCS_CONFIG_FILE = "mkdocs.yml"

DEFAULT_PARADIGM = {
    "quickstart": "Getting Started quickly with the project.",
    "setups": "Installation and configuration guide.",
    "assumptions": "Project assumptions and constraints.",
    "alternatives": "Alternative approaches considered.",
    "functionality": "Core features and functionality overview.",
    "architecture": "High-level system architecture and design."
}

# --- Custom File Contents ---

# Content for extra.css
EXTRA_CSS_CONTENT = """
/* Center Markdown Tables (requires md_in_html extension) */
.center-table {
    text-align: center;
}

.md-typeset .center-table :is(td, th):not([align]) {
    /* Reset alignment for table cells */
    text-align: initial;
}
"""

# Content for katex.js (remains unchanged)
KATEX_JS_CONTENT = """
document$.subscribe(({ body }) => {
    renderMathInElement(body, {
        delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false },
            { left: "\\(", right: "\\)", display: false },
            { left: "\\[", right: "\\]", display: true },
        ],
    });
});
"""

# --- Who We Are ---
COMPANY_INFO = """
We deliver document automation, data analysis and visualization solutions. 

Visit us at [nolainocr.com](https://nolainocr.com)
"""

# Content for README.md
README_MD_CONTENT = f"""
# Project Name

## Description of the project

Welcome to the documentation for this project.

## Project Documentation

- [Quickstart](quickstart/index.md): Getting Started quickly with the project.
- [Setups](setups/index.md): Installation and configuration guide.
- [Functionality](functionality/index.md): Core features and functionality overview.

## Contributing

Please refer to the project's repository for contribution guidelines.

## Who we are?

{COMPANY_INFO}

---
This project documentation was generated using the [https://github.com/nolain-repos/code-docs-generator](code-docs-generator) repo
"""

# Template for mkdocs.yml (Updated with all user requirements and using placeholder)
MKDOCS_YML_TEMPLATE = """
site_name: {site_name_placeholder}
theme:
  icon:
    admonition:
      example: simple/libreofficemath
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.path
    - content.footnote.tooltips
    - content.code.copy
    - content.code.select
    - content.code.annotate
  language: en
  palette:
    # Palette toggle for light mode
    - scheme: default
      primary: indigo
      toggle:
        icon: material/lightbulb
        name: Switch to dark mode

    # Palette toggle for dark mode
    - scheme: slate
      primary: lime
      toggle:
        icon: material/lightbulb-outline
        name: Switch to light mode

markdown_extensions:
  - def_list
  - footnotes
  - pymdownx.critic
  - pymdownx.caret
  - pymdownx.keys
  - pymdownx.mark
  - pymdownx.tilde
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - attr_list
  - pymdownx.emoji
  - pymdownx.tasklist:
      custom_checkbox: true
  - md_in_html
  - pymdownx.arithmatex:
      generic: true
extra:
  annotate:
    json: [.s2]
plugins:
  - search
  - mkdocstrings
  - glightbox
  - mkdocs-jupyter
extra_css:
  - stylesheets/extra.css
  - https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.7/katex.min.css
extra_javascript:
  - javascripts/katex.js
  - https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.7/katex.min.js
  - https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.7/contrib/auto-render.min.js

nav:
  - Home: README.md
"""
